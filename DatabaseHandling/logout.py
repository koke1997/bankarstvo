from flask_login import logout_user


def logout_func():
    # Log out the current user
    logout_user()
