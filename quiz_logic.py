from flask import Blueprint, render_template, request, redirect, url_for
import csv
import random


# Create a blueprint for the quiz logic
quiz_routes = Blueprint('quiz_routes', __name__)

# Global variables to track the quiz state
current_question = 0
questions = []
answers = []  # To track which questions were answered correctly or incorrectly
total_score = 0  # To track the total score
current_component = "Introduction to Defense Mechanisms"  # Start with Knowledge Component 1
skill_levels = {"Introduction to Defense Mechanisms": 0, "Innate Immunity": 0, "Adaptive Immunity": 0, "Immunity Types": 0, "Blood Groups and Rh Factors": 0, "Viruses and Bacteria": 0}

def load_questions_from_csv():
    """Load questions, answers, and options from a CSV file filtered by the knowledge component."""
    global questions
    questions = []
    with open("questions.csv", mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Filter questions by the specified knowledge component
            if row["KnowledgeComponent"] == current_component:
                options = [row["CorrectAnswer"], row["Option1"], row["Option2"], row["Option3"]]
                random.shuffle(options)  # Randomize the order of options
                question_data = {
                    "component": row["KnowledgeComponent"],
                    "question": row["Question"],
                    "correct_answer": row["CorrectAnswer"],
                    "options": options,
                    "feedback": {  
                        row["Option1"]: row["FeedbackOption1"],
                        row["Option2"]: row["FeedbackOption2"],
                        row["Option3"]: row["FeedbackOption3"],
                        row["CorrectAnswer"]: "Correct! Well done."  # Add feedback for correct answer
                    }
                }
                questions.append(question_data)


@quiz_routes.route('/')
def home():
    """Load the questions for the specified knowledge component and start the quiz."""
    global current_question, answers, total_score, skill_levels
    current_question = 0  # Start from the first question
    answers = []  # Reset answers for a new session
    total_score = 0  # Reset the total score

    # Reset skill levels
    skill_levels = {component: 0 for component in skill_levels.keys()}

    # Load questions for the specified component
    load_questions_from_csv()

    return redirect(url_for('quiz_routes.quiz'))


@quiz_routes.route('/quiz')
def quiz():
    """Quiz route to display each question."""
    global current_question

    if current_question < len(questions):
        question = questions[current_question]["question"]
        options = questions[current_question]["options"]
        return render_template('quiz.html', question=question, options=options, current_question=current_question, total=len(questions), answers=answers, score=total_score, skill_levels=skill_levels)
    else:
        return redirect(url_for('quiz_routes.results'))


@quiz_routes.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Handle the answer submission and store feedback."""
    global current_question, answers, total_score, skill_levels
    user_answer = request.form['user_answer']
    correct_answer = questions[current_question]["correct_answer"]
    
    component = questions[current_question]["component"]
    feedback = questions[current_question]['feedback'][user_answer]

    if user_answer == correct_answer:
        total_score += 1
        skill_levels[component] += 1  # Increase the skill level for the current component
        answers.append({"question": questions[current_question]["question"], "result": "Correct", "selected": user_answer, "feedback": feedback})
    else:
        answers.append({"question": questions[current_question]["question"], "result": "Incorrect", "selected": user_answer, "feedback": feedback})

    return render_template('quiz.html', question=questions[current_question]["question"], options=questions[current_question]["options"], 
                           current_question=current_question, total=len(questions), answers=answers, feedback=feedback, selected=user_answer, score=total_score, show_feedback=True, skill_levels=skill_levels)


@quiz_routes.route('/next_question', methods=['POST'])
def next_question():
    """Proceed to the next question after showing feedback."""
    global current_question
    current_question += 1
    return redirect(url_for('quiz_routes.quiz'))


@quiz_routes.route('/results')
def results():
    """Show the final results of the quiz, highlighting correct and incorrect answers and skill levels."""
    return render_template('results.html', answers=answers, score=total_score, skill_levels=skill_levels)
