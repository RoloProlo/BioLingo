import csv
import random
import json
from flask import Blueprint, render_template, request, redirect, url_for

prequiz = Blueprint('prequiz', __name__, template_folder='templates')

# Path to the stereotypes CSV file
STEREOTYPES_FILE = 'data/stereotypes.csv'

def load_stereotypes():
    stereotypes = {}
    try:
        with open(STEREOTYPES_FILE, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                topic, level = row
                stereotypes[topic.strip('"')] = level
    except FileNotFoundError:
        stereotypes = {
            "1.1": "novice",
            "1.2": "novice",
            "1.3": "novice"
        }
    return stereotypes

def save_stereotypes(stereotypes):
    print("Saving stereotypes to CSV...")  # Debugging: Start of save
    with open(STEREOTYPES_FILE, mode='w', newline='') as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        for topic, level in stereotypes.items():
            print(f"Saving: Topic = {topic}, Level = {level}")  # Debugging: Save each topic
            csv_writer.writerow([topic, level])
    print("Stereotypes saved successfully.\n")  # Debugging: End of save

def load_prequiz_data():
    questions_data = []
    csv_file_path = "data/prequiz.csv"
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            topic = row['Topic']
            question = row['Question']
            options = [row['Answer'], row['Option1'], row['Option2'], row['Option3']]
            random.shuffle(options)
            questions_data.append({
                'topic': topic,
                'question': question,
                'options': options,
                'correct_answer': row['Answer']
            })
    return questions_data

@prequiz.route('/prequiz', methods=['GET', 'POST'])
def prequiz_route():
    questions = load_prequiz_data()
    stereotypes = load_stereotypes()

    if request.method == 'POST':
        selected_option = request.form.get('option')
        current_index = int(request.form.get('current_index'))
        
        # Retrieve topic_scores from the form, ensure persistence between requests
        topic_scores = json.loads(request.form.get('topic_scores') or '{}')
        

        # Track score for the current topic
        current_topic = questions[current_index]['topic']
        is_correct = selected_option == questions[current_index]['correct_answer']
        
        # Debugging: Show the current topic and whether the answer was correct
        print(f"Question {current_index + 1} - Topic: {current_topic}, Selected Option: {selected_option}, Correct: {is_correct}")

        # Increment topic score if the answer is correct
        if is_correct:
            if current_topic in topic_scores:
                topic_scores[current_topic] += 1
            else:
                topic_scores[current_topic] = 1

        # Debugging: Show topic scores after each question
        print(f"Topic Scores after question {current_index + 1}: {topic_scores}")

        # Move to the next question
        current_index += 1
        if current_index >= len(questions):
            # Quiz is completed; update level for each topic based on pairs of questions
            for topic, correct_count in topic_scores.items():
                if correct_count >= 2:  # If both questions for the topic were correct
                    stereotypes[topic] = "advanced"
                else:
                    stereotypes[topic] = "novice"
                # Debugging: Show each topic level update
                print(f"Updating Topic '{topic}' to Level '{stereotypes[topic]}' based on correct count of {correct_count}")
                
            save_stereotypes(stereotypes)

            # Redirect to home or results page
            return redirect(url_for('home.home_route'))

        # Render the next question
        return render_template(
            'prequiz.html',
            question=questions[current_index],
            current_index=current_index,
            topic_scores=json.dumps(topic_scores),  # Persist topic_scores across requests
            total=len(questions)
        )

    # Initial GET request to start the quiz
    current_index = 0
    topic_scores = {}
    return render_template(
        'prequiz.html',
        question=questions[current_index],
        current_index=current_index,
        topic_scores=json.dumps(topic_scores),  # Initialize as JSON
        total=len(questions)
    )
