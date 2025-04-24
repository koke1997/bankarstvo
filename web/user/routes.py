# user blueprint routes definition
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user, login_required

# Import services from core directory
from core.services.user_service import authenticate_user, register_new_user, get_user_profile

# Create blueprint with new naming convention
user_bp = Blueprint('user', __name__, template_folder='templates')

@user_bp.route('/', methods=['GET'])
def index():
    """User dashboard or landing page."""
    return render_template('user/index.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Ensure values aren't None before authentication
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('user/login.html')
            
        # Use service layer for authentication
        user, error = authenticate_user(username, password)
        
        if user and not error:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.index'))
        
        flash(error or 'Invalid username or password', 'danger')
    
    return render_template('user/login.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Ensure all values aren't None before registration
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('user/register.html')
            
        # Use service layer for registration
        user, error = register_new_user(username, email, password)
        
        if user and not error:
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('user.login'))
        
        flash(error or 'Registration failed', 'danger')
    
    return render_template('user/register.html')

@user_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    user_profile = get_user_profile(current_user.id)
    return render_template('user/profile.html', profile=user_profile)