import traceback

#DatabaseHandling/authentication.py
from utils.extensions import bcrypt
from core.models import User
from flask_login import login_user, logout_user
from flask import session

def login_func(username, password):
    try:
        print(f"Attempting to log in with username {username} and password {password}")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            print("Login successful")
            return True
        else:
            print("Login failed")
            return False
    except Exception as e:
        print(f"An error occurred during login: {e}")
        traceback.print_exc()
        return False

def logout_func():
    logout_user()