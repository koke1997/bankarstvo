# user_routes/login.py

from flask import Blueprint, request, flash, redirect, url_for, render_template
from DatabaseHandling.authentication import login_func
import traceback
import logging

logger = logging.getLogger(__name__)

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if login_func(username, password):
                flash("Logged in successfully!", "success")

                # Debugging: Log the URL you're redirecting to
                next_url = url_for("account_routes.dashboard")
                logging.info(f"Redirecting to: {next_url}")

                return redirect(next_url)
            else:
                flash("Invalid credentials. Please try again!", "danger")
        return render_template("login.html")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        raise