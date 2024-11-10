import csv
import random
import json
from home import load_completed_kcs
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for

kcquiz = Blueprint('kcquiz', __name__, template_folder='templates')
STEREOTYPES_FILE = 'data/stereotypes.csv'
ANSWERS_FILE = 'data/answers_log.csv' 

TOPIC_MAPPING = {
    "1": "Introduction to Defense Mechanisms",
    "2": "Innate Immunity",
    "3": "Adaptive Immunity",
    "4": "Immunity",
    "5": "Blood Groups and Rh Factors",
    "6": "Viruses and Bacteria"
}

def load_stereotype_level(topic):
    try:
        with open(STEREOTYPES_FILE, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) < 2:
                    continue  
                csv_topic, level = row
                csv_topic = csv_topic.strip('"').strip().lower()
                topic = topic.strip().lower()             
                
                
                if csv_topic == topic:
                    return level.strip('"').strip().lower() 
    except FileNotFoundError:
        pass
    return "novice" 



def load_kcquiz_data(topic, kc, limit=2):
    questions_data = []
    csv_file_path = "data/kcquiz.csv"

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:

            # Extract topic and kc identifiers from the CSV row
            row_topic, row_kc = row['KC'].split('.')

            # Normalize topic and KC for comparison
            row_topic = row_topic.strip().lower()
            row_kc = row_kc.strip().lower()
            topic = topic.strip().lower()
            kc = kc.strip().lower() if kc else ""

            # Debug print for comparison

            # Check if both topic and KC match
            if row_topic == topic and (not kc or row_kc == kc):
                options = [row['CorrectAnswer'], row['Option1'], row['Option2'], row['Option3']]
                random.shuffle(options)
                questions_data.append({
                    "question": row['Question'],
                    "options": options,
                    "correct_answer": row['CorrectAnswer'],
                    "feedback": {
                        row['Option1']: row['FeedbackOption1'],
                        row['Option2']: row['FeedbackOption2'],
                        row['Option3']: row['FeedbackOption3'],
                        row['CorrectAnswer']: "Correct! Well done."
                    }
                })
                # Stop after reaching the limit
                if len(questions_data) >= limit:
                    break


    return questions_data


# Function to log each answer to a CSV file
def log_answer_to_csv(kc, question, given_answer, correct_answer, is_correct, first_try):
    records = []
    question_id = f"{kc}_{question}"  # Using kc and question as a unique identifier

    # Read existing records to find and update the current question if it exists
    try:
        with open(ANSWERS_FILE, mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                existing_question_id = f"{row[0]}_{row[1]}"
                if existing_question_id == question_id:
                    # Update the record for this question
                    records.append([kc, question, given_answer, correct_answer, is_correct, first_try])
                else:
                    # Keep the existing record
                    records.append(row)
    except FileNotFoundError:
        # If the file doesn't exist yet, proceed with an empty list
        pass

    # If the question wasn't found in the existing records, append it
    if not any(f"{row[0]}_{row[1]}" == question_id for row in records):
        records.append([kc, question, given_answer, correct_answer, is_correct, first_try])

    # Write back all records to the CSV file
    with open(ANSWERS_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(records)



@kcquiz.route('/kcquiz/<kc>', methods=['GET', 'POST'])
def kcquiz_route(kc):
    try:
        # Extract the topic key using the TOPIC_MAPPING dictionary
        topic_key = kc.split('.')[0]
        specific_kc = kc.split('.')[1] if len(kc.split('.')) > 1 else None

        topic = topic_key


        stereotype_level = load_stereotype_level(TOPIC_MAPPING.get(topic_key))

        # Debug print to verify stereotype level
        print(f"Stereotype level determined: {stereotype_level}")

    except ValueError:
        return "Invalid KC format", 400

    # Load questions based on topic key and specific knowledge component
    questions = load_kcquiz_data(topic, specific_kc)


    if not questions:
        return render_template('kcquiz_error.html', message=f"No questions available for KC: {kc}")

    

    # Initialize results list to collect question outcomes
    results = request.form.get('results')
    if results:
        results = json.loads(results)
    else:
        results = []

    # Initialize score and current index
    current_index = int(request.form.get('current_index', 0))
    score = int(request.form.get('score', 0))
    attempts = int(request.form.get('attempts', 0))

    if request.method == 'POST':
        # Handle the click on the "Next" button after feedback is shown
        if request.form.get('is_next') == 'true':
            current_index += 1
            if current_index >= len(questions):
                # Redirect to results page if all questions are answered
                return redirect(url_for('kcquiz.kcquiz_result', kc=kc, score=score, total=len(questions), results=json.dumps(results)))

            # Render the next question
            return render_template(
                'kcquiz.html',
                question=questions[current_index],
                current_index=current_index,
                score=score,
                total=len(questions),
                kc=kc,
                stereotype_level=stereotype_level,
                show_feedback=False,
                feedback=None,
                disable_options=False,
                button_text="Submit",
                results=json.dumps(results),
                attempts=0
            )

        # Handle submission of an answer
        selected_option = request.form.get('option', None)

        # If no option is selected, prompt the user to select an answer
        if selected_option is None:
            return render_template(
                'kcquiz.html',
                question=questions[current_index],
                current_index=current_index,
                score=score,
                total=len(questions),
                kc=kc,
                stereotype_level=stereotype_level,
                show_feedback=True,
                feedback="Please select an answer before submitting.",
                disable_options=False,
                button_text="Submit",
                results=json.dumps(results),
                attempts=attempts
            )

        # Check correctness of answer
        question = questions[current_index]
        correct_answer = question['correct_answer']
        is_correct = selected_option == correct_answer

        # Handle advanced user's incorrect response on first attempt
        if stereotype_level == "advanced" and not is_correct and attempts == 0:
            # Provide minimal feedback and allow retry for the advanced user
            feedback = "Wrong, try again."
            return render_template(
                'kcquiz.html',
                question=question,
                current_index=current_index,
                score=score,
                total=len(questions),
                kc=kc,
                stereotype_level=stereotype_level,
                show_feedback=True,
                feedback=feedback,
                disable_options=False,  # Allow options to be selected again
                button_text="Try Again",  # Update button text to "Try Again"
                results=json.dumps(results),
                attempts=attempts + 1
            )

        # Update score if the answer is correct
        if is_correct:
            score += 1

        # Log the user's answer, including whether it's the first try
        first_try = attempts == 0  # True if it's the user's first attempt for this question
        log_answer_to_csv(kc, question['question'], selected_option, correct_answer, is_correct, first_try)

        # Append result to the results list
        results.append({
            'question': question['question'],
            'given_answer': selected_option,
            'correct_answer': correct_answer,
            'feedback': question['feedback'][selected_option] if not is_correct else "Correct! Well done.",
            'is_correct': is_correct
        })

        # Handle incorrect response on second attempt for advanced users
        if not is_correct and stereotype_level == "advanced" and attempts > 0:
            feedback = question['feedback'][selected_option]
            return render_template(
                'kcquiz.html',
                question=question,
                current_index=current_index,
                score=score,
                total=len(questions),
                kc=kc,
                stereotype_level=stereotype_level,
                show_feedback=True,
                feedback=feedback,
                disable_options=True, 
                button_text="Next", 
                results=json.dumps(results),
                attempts=attempts + 1
            )

        feedback = "Correct! Well done." if is_correct else question['feedback'][selected_option]
        return render_template(
            'kcquiz.html',
            question=question,
            current_index=current_index,
            score=score,
            total=len(questions),
            kc=kc,
            stereotype_level=stereotype_level,
            show_feedback=True,
            feedback=feedback,
            disable_options=True,
            button_text="Next",  
            results=json.dumps(results),
            attempts=attempts + 1
        )

    return render_template(
        'kcquiz.html',
        question=questions[current_index],
        current_index=current_index,
        score=score,
        total=len(questions),
        kc=kc,
        stereotype_level=stereotype_level,
        show_feedback=False,
        feedback=None,
        disable_options=False,
        button_text="Submit",
        results=json.dumps(results),
        attempts=0
    )

def save_completed_kc(kc):
    truncated_kc = ".".join(kc.split(".")[:2])

    csv_file_path = 'data/completed_kcs.csv'
    completed_kcs = set(load_completed_kcs())  
    completed_kcs.add(truncated_kc)  

    print(f"Saving KC: {truncated_kc} to completed_kcs.csv")  
    with open(csv_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        for kc in completed_kcs:
            csv_writer.writerow([kc])



@kcquiz.route('/kcquiz_result/<kc>', methods=['GET'])
def kcquiz_result(kc):
    score = int(request.args.get('score', 0))
    total = int(request.args.get('total', 0))
    results = json.loads(request.args.get('results', '[]'))

    save_completed_kc(kc)


    csv_results = []
    try:
        with open(ANSWERS_FILE, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == kc: 
                    csv_results.append({
                        'question': row[1],
                        'given_answer': row[2],
                        'correct_answer': row[3],
                        'is_correct': row[4] == 'True'
                    })
    except FileNotFoundError:
        pass 
    return render_template(
        'kcquiz_result.html',
        score=score,
        total=total,
        kc=kc,
        results=csv_results
    )
