
from extensions import bcrypt
from models import User
from flask_login import login_user, logout_user

def login_func(email, password):
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return True
    return False

def logout_func():
    logout_user()
