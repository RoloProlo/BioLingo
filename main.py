from flask import Flask
from home_logic import home_routes  # Import the home logic blueprint
from quiz_logic import quiz_routes  # Import the quiz logic blueprint

# Initialize the Flask application
app = Flask(__name__)

# Register the blueprints for home and quiz logic separately
app.register_blueprint(home_routes)
app.register_blueprint(quiz_routes, url_prefix='/quiz')  # Use /quiz for all quiz-related routes

if __name__ == '__main__':
    app.run(debug=True)
