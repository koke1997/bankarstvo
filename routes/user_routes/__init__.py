# user_routes/__init__.py
from flask import Blueprint, render_template

user_routes = Blueprint('user_routes', __name__)

# Import route functions
from .views import index
from .login import login
from .register import register
from .logout import logout

# Register route functions
user_routes.add_url_rule('/', endpoint='index', view_func=index)
user_routes.add_url_rule('/login', endpoint='login', view_func=login)
user_routes.add_url_rule('/register', endpoint='register', view_func=register)
user_routes.add_url_rule('/logout', endpoint='logout', view_func=logout)
