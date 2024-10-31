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

@lesson.route('/lessons/<kc>', methods=['GET'])
def lessons_by_kc(kc):
    # Load all lessons from the CSV file
    csv_file_path = "data/lessons.csv"
    lessons = []

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['KC'].startswith(kc):
                lessons.append({
                    'kc': row['KC'],
                    'text': row['text'],
                    'title': row['title']
                })

    # If lessons are found, start with the first lesson
    if lessons:
        current_index = 0
        current_lesson = lessons[current_index]

        return render_template(
            'lesson.html',
            lesson_text=current_lesson['text'],
            current_index=current_index,
            current_kc=current_lesson['kc'],
            disable_back=True,
            disable_next=len(lessons) == 1,
            is_last_in_section=len(lessons) == 1
        )

    # If no lessons found, handle gracefully (e.g., show an error page or message)
    return "No lessons found for this KC", 404



@lesson.route('/lesson', methods=['GET', 'POST'])
def lesson_route():
    kc_prefix = request.args.get('kc') or request.form.get('kc')
    current_index = int(request.form.get('current_index', 0))

    # Load all lessons that match the given KC prefix
    csv_file_path = "data/lessons.csv"
    lessons = []

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['KC'].startswith(kc_prefix):
                lessons.append({
                    'kc': row['KC'],
                    'text': row['text'],
                    'title': row['title']
                })

    # Determine which lesson to show based on current index
    if request.method == 'POST':
        if 'next' in request.form and current_index < len(lessons) - 1:
            current_index += 1
        elif 'back' in request.form and current_index > 0:
            current_index -= 1

    # Get the current lesson content
    current_lesson = lessons[current_index]

    # Determine if navigation buttons should be disabled
    disable_back = current_index == 0
    disable_next = current_index == len(lessons) - 1
    is_last_in_section = current_index == len(lessons) - 1

    return render_template(
        'lesson.html',
        lesson_text=current_lesson['text'],
        current_index=current_index,
        current_kc=current_lesson['kc'],
        disable_back=disable_back,
        disable_next=disable_next,
        is_last_in_section=is_last_in_section
    )
