from flask import Blueprint, render_template
import csv

home = Blueprint('home', __name__, template_folder='templates')


def load_completed_kcs():
    csv_file_path = 'data/completed_kcs.csv'
    completed_kcs = []
    try:
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            completed_kcs = [row[0] for row in csv_reader]
    except FileNotFoundError:
        pass  # If the file doesn't exist yet, return an empty list
    return completed_kcs

@home.route('/home')
def home_route():
    # Load completed KCs from the CSV file
    completed_kcs = load_completed_kcs()
    print(f"Completed KCs loaded: {completed_kcs}")

    # Pass completed KCs to the template
    return render_template('home.html', completed_kcs=completed_kcs)
