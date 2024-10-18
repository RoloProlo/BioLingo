from flask import Flask, render_template
from quiz import load_questions_for_component  # Importing the function from quiz.py
from quiz import quiz_routes  # Import the quiz Blueprint
from prequiz import load_prequiz_data
from shared import skill_levels, component_order  # Import skill_levels from shared.py
from prequiz import prequiz  # Import the prequiz Blueprint
from home import home  # Import the home blueprint

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(quiz_routes)
app.register_blueprint(prequiz, url_prefix='/prequiz')
app.register_blueprint(home, url_prefix='/home')


@app.route('/')
def welcome():
    return render_template('start.html')


@app.route('/prequiz')
def prequiz_route():
    current_index = 0
    score = 0
    questions = load_prequiz_data()

    if not questions:
        return "No questions available."

    return render_template(
        'prequiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions)
    )


@app.route('/home')
def home():
    global current_question, score, answers, questions
    # Reset the quiz state
    current_question = 0
    score = 0
    answers = []
    questions = []
    enumerated_components = list(enumerate(component_order))
    return render_template('home.html', skill_levels=skill_levels, component_order=enumerated_components)

if __name__ == "__main__":
    app.run(debug=True)
