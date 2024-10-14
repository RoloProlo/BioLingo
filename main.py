from flask import Flask, render_template
from quiz import load_questions_for_component  # Importing the function from quiz.py
from quiz import quiz_routes  # Import the quiz Blueprint



app = Flask(__name__)
app.register_blueprint(quiz_routes)


# Initialize skill levels for each knowledge component
skill_levels = {
    "Introduction to Defense Mechanisms": 0, 
    "Innate Immunity": 0,
    "Adaptive Immunity": 0,
    "Immunity Types": 0,
    "Blood Groups and Rh Factors": 0,
    "Viruses and Bacteria": 0
}

@app.route('/')
def home():
    global current_question, score, answers
    # Reset the quiz state
    current_question = 0
    score = 0
    answers = []
    return render_template('home.html', skill_levels=skill_levels)


@app.route('/quiz/<component>')
def quiz(component):
    # Load questions for the selected component from the CSV using the function in quiz.py
    questions = load_questions_for_component(component)
    return render_template('quiz.html', component=component, questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
