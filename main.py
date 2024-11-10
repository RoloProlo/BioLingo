from flask import Flask, render_template, redirect, url_for
from prequiz import load_prequiz_data, prequiz 
from home import home  
from lesson import lesson 
from kcquiz import kcquiz 



app = Flask(__name__)

# Register Blueprints
app.register_blueprint(prequiz, url_prefix='/prequiz')
app.register_blueprint(home, url_prefix='/home')
app.register_blueprint(lesson, url_prefix='/lesson') 
app.register_blueprint(kcquiz, url_prefix='/kcquiz')  




@app.route('/')
def welcome():
    return render_template('start.html')


@app.route('/prequiz')
def prequiz_route():
    current_index = 0
    score = 0
    questions = load_prequiz_data()
    selected_options = {} 

    if not questions:
        return "No questions available."

    return render_template(
        'prequiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions),
        selected_options=selected_options 
    )


@app.route('/home')
def home_route():
    return redirect(url_for('home.home_route'))


if __name__ == "__main__":
    app.run(debug=True)
