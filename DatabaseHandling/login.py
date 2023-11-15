
from extensions import bcrypt
from models import User
from flask_login import login_user, logout_user

def login_func(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):  # Notice the field is password_hash
        login_user(user)
        return True
    return False


def logout_func():
    logout_user()
