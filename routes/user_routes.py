from flask import Blueprint, render_template, request, redirect, url_for, flash
from DatabaseHandling.login import login_func, logout_func
from DatabaseHandling.registration import register_user
from models import User


user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@user_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_func(username, password):
            flash('Logged in successfully!', 'success')
            return redirect(url_for('account_routes.dashboard'))
        else:
            flash('Invalid credentials. Please try again!', 'danger')
    return render_template('login.html')

@user_routes.route('/register', methods=['GET', 'POST'])
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

@user_routes.route('/logout', methods=['GET'])
def logout():
    logout_func()
    return redirect(url_for('user_routes.login'))

def configure_user_routes(app):
    app.register_blueprint(user_routes)
