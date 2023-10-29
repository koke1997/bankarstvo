from app import db, bcrypt
from flask import Blueprint, render_template, request, flash, redirect, url_for

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store the user in the database
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login.index'))

    return render_template('register.html')
