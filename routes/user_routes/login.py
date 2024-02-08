# user_routes/login.py

from flask import Blueprint, request, flash, redirect, url_for, render_template
from DatabaseHandling.login import login_func
from routes.account_routes.dashboard import dashboard

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/user/login', methods=['GET', 'POST'], endpoint="login")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_func(username, password):
            flash('Logged in successfully!', 'success')
            
            # Debugging: Print the URL you're redirecting to
            next_url = url_for('account_routes.dashboard')
            print(f"Redirecting to: {next_url}")
            
            return redirect(next_url)
        else:
            flash('Invalid credentials. Please try again!', 'danger')
    return render_template('login.html')
