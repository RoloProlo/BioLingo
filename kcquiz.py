import csv
import random
from flask import Blueprint, render_template, request, redirect, url_for, session

# Create a new Blueprint for KCquiz
kcquiz = Blueprint('kcquiz', __name__, template_folder='templates')

# Function to load questions based on the major KC
def load_kcquiz_data(major_kc):
    questions_data = []
    csv_file_path = "data/kcquiz.csv"

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Extract the major KC from the row (e.g., 1.1 from 1.1.1)
            row_major_kc = row['KC'].split('.')[0] + '.' + row['KC'].split('.')[1]
            
            if row_major_kc == major_kc:  # Match only the major KC
                options = [row['CorrectAnswer'], row['Option1'], row['Option2'], row['Option3']]
                random.shuffle(options)  # Randomize the order of options
                questions_data.append({
                    "question": row['Question'],
                    "options": options,
                    "correct_answer": row['CorrectAnswer'],
                    "feedback": {
                        row['Option1']: row['FeedbackOption1'],
                        row['Option2']: row['FeedbackOption2'],
                        row['Option3']: row['FeedbackOption3'],
                        row['CorrectAnswer']: "Correct! Well done."
                    }
                })

    return questions_data

# Route for handling the quiz page
@kcquiz.route('/kcquiz/<kc>', methods=['GET', 'POST'])
def kcquiz_route(kc):
    # Extract the major KC from the current KC (e.g., 1.1 from 1.1.1)
    major_kc = kc.split('.')[0] + '.' + kc.split('.')[1]

    # Load the questions for the given major KC
    questions = load_kcquiz_data(major_kc)

    # Check if there are no questions for the KC
    if not questions:
        return render_template('kcquiz_error.html', message=f"No questions available for KC: {major_kc}")

    if request.method == 'POST':
        selected_option = request.form.get('option')
        current_index = int(request.form.get('current_index'))
        score = int(request.form.get('score'))

        # Check if we are out of bounds for the question index
        if current_index >= len(questions):
            # Redirect to the result page and pass the KC along with the score and total
            return redirect(url_for('kcquiz.kcquiz_result', score=score, total=len(questions), kc=kc))

        # Check the answer
        if selected_option == questions[current_index]['correct_answer']:
            score += 1

        # Move to the next question
        current_index += 1
        if current_index >= len(questions):
            # If there are no more questions, redirect to the results page
            return redirect(url_for('kcquiz.kcquiz_result', score=score, total=len(questions), kc=kc))

        # Render the next question
        return render_template(
            'kcquiz.html',
            question=questions[current_index],
            current_index=current_index,
            score=score,
            total=len(questions),
            kc=kc  # Pass kc to the template
        )

    # Start the quiz from the first question
    current_index = 0
    score = 0
    return render_template(
        'kcquiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions),
        kc=kc  # Pass kc to the template
    )

# Save the completed KC to a CSV file
# Save the completed KC to a CSV file, only saving the first two parts of the KC (e.g., 1.1 from 1.1.3)
def save_completed_kc(kc):
    # Extract the first two parts of the KC (e.g., 1.1 from 1.1.3)
    major_kc = kc.split('.')[0] + '.' + kc.split('.')[1]
    
    csv_file_path = 'data/completed_kcs.csv'
    
    # Check if the KC is already saved, if not, save it
    existing_kcs = set()
    try:
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            existing_kcs = {row[0] for row in csv_reader}
    except FileNotFoundError:
        pass  # If the file doesn't exist yet, create it

    if major_kc not in existing_kcs:
        # Append the major KC to the CSV file if not already there
        with open(csv_file_path, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([major_kc])


@kcquiz.route('/kcquiz/result')
def kcquiz_result():
    score = request.args.get('score')
    total = request.args.get('total')

    # Get the current KC from query parameters and save it to the CSV file
    current_kc = request.args.get('kc')
    save_completed_kc(current_kc)
    return render_template('kcquiz_result.html', score=score, total=total)
