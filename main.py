from flask import Flask
from quiz_logic import quiz_routes  # Import the quiz logic blueprint

# Initialize the Flask application
app = Flask(__name__)

# Register the blueprint from quiz_logic.py
app.register_blueprint(quiz_routes)

if __name__ == '__main__':
    app.run(debug=True)
