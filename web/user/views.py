# user_routes/index.py
from . import user_routes
from flask import render_template

@user_routes.route('/')
def index():
    return render_template('index.html')
