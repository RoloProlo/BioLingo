import csv
import random
from flask import Blueprint, request, render_template, redirect, url_for

quiz_routes = Blueprint('quiz', __name__)  # Blueprint definition

answers = []  # List to keep track of user answers and results
current_question = 0
score = 0


# Function to load questions from the CSV based on the knowledge component
def load_questions_for_component(component):
    questions = []
    with open('questions.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['KnowledgeComponent'] == component:
                options = [row['CorrectAnswer'], row['Option1'], row['Option2'], row['Option3']]
                random.shuffle(options)  # Randomize the order of options
                questions.append({
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
    return questions

# Function to submit the user's answer and provide feedback
def submit_answer(user_answer, correct_answer, current_question, questions):
    feedback = questions[current_question]['feedback'][user_answer]

    if user_answer == correct_answer:
        result = "Correct!"
    else:
        result = "Incorrect"

    return {
        'result': result,
        'feedback': feedback,
        'correct_answer': correct_answer,
        'user_answer': user_answer
    }

# Route for starting the quiz
@quiz_routes.route('/quiz/<component>')
def quiz(component):
    global questions, current_question
    questions = load_questions_for_component(component)
    # Uncommented this block to handle the end of the quiz properly:
    if current_question >= len(questions):
        return redirect(url_for('home'))  # If no more questions, go to home screen

    question = questions[current_question]['question']
    options = questions[current_question]['options']
    return render_template('quiz.html', question=question, options=options, current_question=current_question)

# Route for submitting the answer
@quiz_routes.route('/submit_answer', methods=['POST'])
def handle_submit():
    global current_question, score, answers
    user_answer = request.form['user_answer']
    correct_answer = questions[current_question]['correct_answer']
    result_data = submit_answer(user_answer, correct_answer, current_question, questions)

    # Add the current question and result to the answers list
    answers.append({
        "question": questions[current_question]["question"],
        "result": result_data["result"],
        "feedback": result_data["feedback"]
    })

    # If the answer is correct, increase the score
    if result_data['result'] == "Correct!":
        score += 1

    # Show feedback and allow moving to the next question
    return render_template('quiz.html',
                           question=questions[current_question]['question'],
                           options=questions[current_question]['options'],
                           current_question=current_question,
                           feedback=result_data['feedback'],
                           correct_answer=result_data['correct_answer'],  # Pass correct answer
                           user_answer=result_data['user_answer'],  # Pass user's answer
                           show_feedback=True)  # Enable feedback display


# Route to move to the next question
@quiz_routes.route('/next_question', methods=['POST'])
def next_question():
    global current_question, answers

    current_question += 1

    # Check if there are still more questions
    if current_question < len(questions):
        question = questions[current_question]['question']
        options = questions[current_question]['options']
        return render_template('quiz.html', 
                               question=question, 
                               options=options, 
                               current_question=current_question, 
                               total=len(questions),
                               show_feedback=False)
    else:
        # No more questions, render the results
        return render_template('results.html', 
                               answers=answers,  # List of answered questions with feedback
                               score=score,      # Total score
                               total=len(questions))  # Total number of questions

