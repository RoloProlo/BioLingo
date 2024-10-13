# home_logic.py
from flask import Blueprint, render_template

# Create a blueprint for home logic
home_routes = Blueprint('home_routes', __name__)

# Define a simple route for the home page
@home_routes.route('/')
def home():
    """Render the home screen as the main landing page."""
    # Skill levels should be in percentages (0-100)
    skill_levels = {
        "Introduction to Defense Mechanisms": 30,  # 30% completed
        "Innate Immunity": 0,
        "Adaptive Immunity": 0,
        "Immunity Types": 0,
        "Blood Groups and Rh Factors": 0,
        "Viruses and Bacteria": 0
    }
    return render_template('home.html', skill_levels=skill_levels)

