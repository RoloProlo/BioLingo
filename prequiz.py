import csv
import random
from flask import Blueprint, render_template, request, redirect, url_for

prequiz = Blueprint('prequiz', __name__, template_folder='templates')

questions = []

def load_prequiz_data():
    questions_data = []

    # Adjust file path as needed
    csv_file_path = "data/prequiz.csv"

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            question = row['Question']
            options = [
                row['Answer'],  # The correct answer
                row['Option1'],
                row['Option2'],
                row['Option3']
            ]
            # Shuffle the options to prevent the answer from always being first
            random.shuffle(options)
            questions_data.append({'question': question, 'options': options, 'correct_answer': row['Answer']})

    return questions_data

@prequiz.route('/prequiz', methods=['GET', 'POST'])
def prequiz_route():
    global questions
    questions = load_prequiz_data()

    if request.method == 'POST':
        selected_option = request.form.get('option')
        current_index = int(request.form.get('current_index'))
        score = int(request.form.get('score'))

        # Check the answer
        if selected_option == questions[current_index]['correct_answer']:
            score += 1

        # Move to the next question or finish
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
