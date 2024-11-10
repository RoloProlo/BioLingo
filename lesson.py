from flask import Blueprint, render_template, request
import csv

lesson = Blueprint('lesson', __name__, template_folder='templates')

def load_lesson_data():
    lesson_data = []
    csv_file_path = 'data/lessons.csv'

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            topic = row['KC'].split('.')[0]
            lesson_data.append({
                'kc': row['KC'],
                'topic': topic,  
                'content': row['text'] 
            })
    return lesson_data

@lesson.route('/lessons/<kc>', methods=['GET'])
def lessons_by_kc(kc):
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

    return "No lessons found for this KC", 404



@lesson.route('/lesson', methods=['GET', 'POST'])
def lesson_route():
    kc_prefix = request.args.get('kc') or request.form.get('kc')
    current_index = int(request.form.get('current_index', 0))

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

    if request.method == 'POST':
        if 'next' in request.form and current_index < len(lessons) - 1:
            current_index += 1
        elif 'back' in request.form and current_index > 0:
            current_index -= 1

    current_lesson = lessons[current_index]

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
