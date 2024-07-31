from flask import request, redirect, url_for, flash, render_template
from . import user_routes
from DatabaseHandling.registration_func import register_user
from core.models import User

@user_routes.route('/register', methods=['GET', 'POST'], endpoint="register")
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in instead.', 'danger')
            return redirect(url_for('user_routes.login'))

        # No existing user, proceed with registration
        user = register_user(username, email, password)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user_routes.login'))

    # If not a POST request, just render the registration page
    return render_template('register.html')
