from flask import Flask, render_template, redirect, url_for
from prequiz import load_prequiz_data, prequiz  # Import prequiz blueprint and functions
from home import home  # Import the home blueprint
from lesson import lesson  # Import lesson blueprint
from kcquiz import kcquiz  # Import the new KCquiz Blueprint



app = Flask(__name__)

# Register Blueprints
app.register_blueprint(prequiz, url_prefix='/prequiz')
app.register_blueprint(home, url_prefix='/home')
app.register_blueprint(lesson, url_prefix='/lesson')  # Register with a URL prefix
app.register_blueprint(kcquiz, url_prefix='/kcquiz')  # Register the KCquiz Blueprint




@app.route('/')
def welcome():
    return render_template('start.html')


@app.route('/prequiz')
def prequiz_route():
    current_index = 0
    score = 0
    questions = load_prequiz_data()
    selected_options = {}  # Initialize selected_options as an empty dictionary

    if not questions:
        return "No questions available."

    return render_template(
        'prequiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions),
        selected_options=selected_options  # Pass selected_options on the initial load
    )


@app.route('/home')
def home_route():
    return redirect(url_for('home.home_route'))


if __name__ == "__main__":
    app.run(debug=True)
