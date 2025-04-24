from flask import request, redirect, url_for, flash, render_template
from . import user_routes
from core.models import User
from utils.extensions import db, bcrypt  # Removed token_required

@user_routes.route('/register', methods=['GET', 'POST'], endpoint="register")
# Removed @token_required decorator to make registration accessible
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate inputs are not None
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')

        # Check if user already exists - using db.session.query instead of User.query
        existing_user = db.session.query(User).filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in instead.', 'danger')
            return redirect(url_for('user_routes.login'))

        # No existing user, proceed with registration
        # Generate password hash
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user with keyword arguments
        new_user = User(
            username=username, 
            email=email, 
            password_hash=password_hash
        )
        
        # Add to database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user_routes.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('user_routes.register'))

    # If not a POST request, just render the registration page
    return render_template('register.html')
