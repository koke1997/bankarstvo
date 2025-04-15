# user_routes/login.py

from flask import Blueprint, request, flash, redirect, url_for, render_template
from DatabaseHandling.authentication import login_func
import traceback
import logging
from keycloak import KeycloakOpenID

logger = logging.getLogger(__name__)

user_routes = Blueprint("user_routes", __name__)

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET_KEY")
)

@user_routes.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            token = keycloak_openid.token(username, password)
            if token:
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
