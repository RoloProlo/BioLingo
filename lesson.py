from flask import Blueprint, render_template, request
import csv

lesson = Blueprint('lesson', __name__, template_folder='templates')

# Load CSV content, extracting the topic from the KC
def load_lesson_data():
    lesson_data = []
    csv_file_path = 'data/lessons.csv'

    # Open the CSV and map the headers to KC and text
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Extract the first number from KC to be used as the topic
            topic = row['KC'].split('.')[0]
            lesson_data.append({
                'kc': row['KC'],  # KC column
                'topic': topic,  # Extracted topic from KC
                'content': row['text']  # text column
            })
    return lesson_data

@lesson.route('/lesson', methods=['GET', 'POST'])
def lesson_route():
    lesson_data = load_lesson_data()

    # Determine the current index based on form submission (defaults to 0)
    current_index = int(request.form.get('current_index', 0))

    # Handle "Next" button press
    if request.method == 'POST' and 'next' in request.form:
        current_index += 1
        if current_index >= len(lesson_data):  # Prevent out of range errors
            current_index = len(lesson_data) - 1

    # Handle "Back" button press
    if request.method == 'POST' and 'back' in request.form:
        current_index -= 1
        if current_index < 0:  # Prevent negative index errors
            current_index = 0

    # Get the current and previous topics for comparison
    current_kc = lesson_data[current_index]['kc']  # Extract current KC
    current_major_kc = current_kc.rsplit('.', 1)[0]  # Get the major KC (e.g., "1.1")

    # Check if the next KC belongs to a different major KC (e.g., from "1.1" to "1.2")
    if current_index + 1 < len(lesson_data):
        next_kc = lesson_data[current_index + 1]['kc']
        next_major_kc = next_kc.rsplit('.', 1)[0]
    else:
        next_major_kc = current_major_kc  # If at the end, assume no change

    # Check if the current KC is the last sub-KC of the current major KC
    is_last_in_section = current_major_kc != next_major_kc

    # Disable "Next" button if the next major KC will be different
    disable_next = is_last_in_section

    if current_index - 1 >= 0:
        previous_kc = lesson_data[current_index - 1]['kc']
        previous_major_kc = previous_kc.rsplit('.', 1)[0]
    else:
        previous_major_kc = current_major_kc  # Prevent going to negative index

    # Disable "Back" button if the previous KC belongs to a different major KC
    disable_back = current_major_kc != previous_major_kc

    # Pass data to the template, including the current KC
    return render_template(
        'lesson.html',
        lesson_text=lesson_data[current_index]['content'],
        current_index=current_index,
        disable_next=disable_next,  # Disable next if the current KC is the last sub-KC of the major KC
        disable_back=disable_back,  # Disable back if the previous KC is from a different major KC
        is_last_in_section=is_last_in_section,  # True if it's the last sub-KC in the current major KC
        current_kc=current_kc  # Pass the current KC to the template
    )
