from flask import Blueprint, render_template

# Define a Blueprint for home
home = Blueprint('home', __name__, template_folder='templates')

@home.route('/home')
def home_route():
    # Render the Chapter 1 screen
    return render_template('home.html')
