import csv
import random
from flask import Blueprint, request, render_template, redirect, url_for
from shared import skill_levels  # Import skill_levels from shared.py

quiz_routes = Blueprint('quiz', __name__)  # Blueprint definition

answers = []  # List to keep track of user answers and results
current_question = 0
score = 0

increment_per_question = 0  # Increment value for each correct answer


# Function to load questions from the CSV based on the knowledge component
def load_questions_for_component(component):
    questions = []
    with open('prequiz.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['KC'] == component:
                options = [row['CorrectAnswer'], row['Option1'], row['Option2'], row['Option3']]
                random.shuffle(options)  # Randomize the order of options
                questions.append({
                    "question": row['Question'],
                    "options": options,
                    "correct_answer": row['CorrectAnswer'],
                    "difficulty": float(row['Difficulty']),  # Add difficulty level
                    "feedback": {
                        row['Option1']: row['FeedbackOption1'],
                        row['Option2']: row['FeedbackOption2'],
                        row['Option3']: row['FeedbackOption3'],
                        row['CorrectAnswer']: "Correct! Well done."
                    }
                })
    return questions

@quiz_routes.route('/quiz/<component>')
def quiz(component):
    global questions, current_question, score, answers, current_component, increment_per_question

    # Set the current component being used
    current_component = component

    # Reset current question index when starting a new quiz
    current_question = 0
    score = 0
    answers = []
    questions = load_questions_for_component(component)

    # Calculate the increment per correct answer
    if len(questions) > 0:
        increment_per_question = 100 / len(questions)
    else:
        increment_per_question = 0

    # If no questions are available, redirect to home
    if len(questions) == 0:
        return redirect(url_for('home'))

    # Extract current question details
    question = questions[current_question]['question']
    options = questions[current_question]['options']
    correct_answer = questions[current_question]['correct_answer']

    return render_template('quiz.html', 
                           question=question, 
                           options=options, 
                           current_question=current_question, 
                           correct_answer=correct_answer,  # Pass correct answer to the template
                           total=len(questions))

@quiz_routes.route('/submit_answer', methods=['POST'])
def handle_submit():
    global current_question, score, answers, current_component, skill_levels

    user_answer = request.form['user_answer']
    correct_answer = questions[current_question]['correct_answer']

    # Generate feedback and determine if the answer is correct
    feedback = questions[current_question]['feedback'][user_answer]
    if user_answer == correct_answer:
        result = "Correct!"
        score += 1  # Increment score if correct
        
        # Update skill level for the current component
        skill_levels[current_component] += increment_per_question
        # Ensure skill level does not exceed 100
        if skill_levels[current_component] > 100:
            skill_levels[current_component] = 100
    else:
        result = "Incorrect"

    # Add the current question and result to the answers list
    answers.append({
        "question": questions[current_question]["question"],
        "result": result,
        "feedback": feedback
    })

    print(f"Updated skill level for {current_component}: {skill_levels[current_component]}")

    # Show feedback and allow moving to the next question
    return render_template('quiz.html',
                           question=questions[current_question]['question'],
                           options=questions[current_question]['options'],
                           current_question=current_question,
                           feedback=feedback,
                           correct_answer=correct_answer,  # Pass correct answer
                           user_answer=user_answer,  # Pass user's answer
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
        correct_answer = questions[current_question]['correct_answer']  # Extract correct answer

        return render_template('quiz.html', 
                               question=question, 
                               options=options, 
                               current_question=current_question, 
                               correct_answer=correct_answer,  # Pass correct answer to the template
                               total=len(questions),
                               show_feedback=False)
    else:
        # No more questions, render the results
        return render_template('results.html', 
                               answers=answers,  # List of answered questions with feedback
                               score=score,      # Total score
                               total=len(questions))  # Total number of questions
