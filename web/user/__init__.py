# user_routes/__init__.py
from flask import Blueprint, render_template

user_routes = Blueprint('user_routes', __name__, 
                       template_folder="templates",
                       url_prefix="/user")  # Added URL prefix for better route organization

# Import route functions
from .views import index
from .login import login, callback
from .register import register
from .logout import logout

# Register route functions with explicit methods
user_routes.add_url_rule('/', 
                        endpoint='index', 
                        view_func=index,
                        methods=['GET'])

user_routes.add_url_rule('/login', 
                        endpoint='login', 
                        view_func=login,
                        methods=['GET', 'POST'])

user_routes.add_url_rule('/callback', 
                        endpoint='callback', 
                        view_func=callback,
                        methods=['GET'])

user_routes.add_url_rule('/register', 
                        endpoint='register', 
                        view_func=register,
                        methods=['GET', 'POST'])

user_routes.add_url_rule('/logout', 
                        endpoint='logout', 
                        view_func=logout,
                        methods=['GET'])

# Log registration of user routes
print(f"Registered user routes: {[rule.rule for rule in user_routes.iter_rules()]}")
