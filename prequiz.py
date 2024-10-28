import csv
import random
from flask import Blueprint, render_template, request, redirect, url_for

prequiz = Blueprint('prequiz', __name__, template_folder='templates')

# Path to the stereotypes CSV file
STEREOTYPES_FILE = 'data/stereotypes.csv'

# Function to load stereotypes from CSV
def load_stereotypes():
    stereotypes = {}
    try:
        with open(STEREOTYPES_FILE, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                kc, level = row
                stereotypes[kc.strip('"')] = level  # Remove quotes when loading
    except FileNotFoundError:
        # Initialize with default values if the file doesn't exist
        stereotypes = {
            "1.1": "novice",
            "1.2": "novice",
            "1.3": "novice"
        }
    return stereotypes

# Function to save stereotypes to CSV (with KC in quotes)
def save_stereotypes(stereotypes):
    with open(STEREOTYPES_FILE, mode='w', newline='') as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_ALL)  # Ensure KC is wrapped in quotes
        for kc, level in stereotypes.items():
            csv_writer.writerow([kc, level])

# Load prequiz data from CSV
def load_prequiz_data():
    questions_data = []
    csv_file_path = "data/prequiz.csv"

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            kc = row['KC']  # KC is the first column in your CSV
            question = row['Question']
            options = [row['Answer'], row['Option1'], row['Option2'], row['Option3']]
            random.shuffle(options)  # Shuffle the options to randomize order
            questions_data.append({
                'kc': kc,
                'question': question,
                'options': options,
                'correct_answer': row['Answer']
            })
    return questions_data

# Function to update the skill level for a KC based on correctness
def update_skill_level(kc, correct_answers, stereotypes):
    # Update stereotype based on correct answers
    if correct_answers >= 2:
        stereotypes[kc] = "advanced"
    else:
        stereotypes[kc] = "novice"
    save_stereotypes(stereotypes)  # Save the updated stereotypes to CSV

# Prequiz route to handle the quiz
@prequiz.route('/prequiz', methods=['GET', 'POST'])
def prequiz_route():
    questions = load_prequiz_data()
    stereotypes = load_stereotypes()  # Load the current stereotypes from CSV

    if request.method == 'POST':
        selected_option = request.form.get('option')
        current_index = int(request.form.get('current_index'))
        score = int(request.form.get('score'))

        # Get the current KC
        current_kc = questions[current_index]['kc']

        # Check if the selected option is correct
        if selected_option == questions[current_index]['correct_answer']:
            score += 1

        # Track KC correctness for every 2 questions
        if (current_index + 1) % 2 == 0:  # After every two questions for the same KC
            correct_answers = 0

            # Check last 2 questions to count correct answers
            for i in range(current_index - 1, current_index + 1):
                if request.form.get(f'option_{i}') == questions[i]['correct_answer']:
                    correct_answers += 1

            # Update the skill level based on the correctness of the last 2 questions
            update_skill_level(current_kc, correct_answers, stereotypes)

        # Move to the next question or finish the quiz
        current_index += 1
        if current_index >= len(questions):
            return redirect(url_for('home.home_route'))

        return render_template(
            'prequiz.html',
            question=questions[current_index],
            current_index=current_index,
            score=score,
            total=len(questions)
        )

    # Start with the first question
    current_index = 0
    score = 0
    return render_template(
        'prequiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions)
    )

@prequiz.route('/prequiz/result')
def result():
    score = int(request.args.get('score'))
    total = int(request.args.get('total'))
    return render_template('result.html', score=score, total=total)
