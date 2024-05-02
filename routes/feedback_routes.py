from flask import Blueprint, request, render_template, flash, redirect, url_for
from DatabaseHandling.connection import get_db_cursor

feedback_routes = Blueprint('feedback_routes', __name__)

@feedback_routes.route('/feedback', methods=['GET'])
def feedback_form():
    return render_template('feedback_form.html')

@feedback_routes.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    feedback = request.form.get('feedback')

    try:
        conn, cursor = get_db_cursor()
        cursor.execute("INSERT INTO feedback (name, email, feedback) VALUES (%s, %s, %s)", (name, email, feedback))
        conn.commit()
        flash('Feedback submitted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while submitting your feedback: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('feedback_routes.feedback_form'))
