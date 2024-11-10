from flask import Blueprint, render_template, redirect, url_for
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
        pass  
    return completed_kcs

@home.route('/set_all_novice', methods=['POST'])
def set_all_novice():
    # Set all stereotypes to "novice"
    csv_file_path = "data/stereotypes.csv"
    topics = []

    # Read all topics and set them to novice
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            topic, _ = row
            topics.append([topic, 'novice'])

    # Write updated topics back to the stereotypes CSV
    with open(csv_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['topic', 'level'])  # Write header
        csv_writer.writerows(topics)

    # Redirect to the home page
    return redirect(url_for('home.home_route'))


@home.route('/home')
def home_route():
    # Load completed KCs from the CSV file
    completed_kcs = load_completed_kcs()
    print(f"Completed KCs loaded: {completed_kcs}")

    # Pass completed KCs to the template
    return render_template('home.html', completed_kcs=completed_kcs)



