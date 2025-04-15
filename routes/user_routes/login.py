# user_routes/login.py

from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from DatabaseHandling.authentication import login_func
import traceback
import logging
from keycloak import KeycloakOpenID
import os

logger = logging.getLogger(__name__)

user_routes = Blueprint("user_routes", __name__)

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET_KEY")
)

@user_routes.route("/login", methods=["GET"], endpoint="login")
def login():
    try:
        # Redirect to Keycloak for authentication
        redirect_url = keycloak_openid.auth_url(
            redirect_uri=url_for("user_routes.callback", _external=True)
        )
        return redirect(redirect_url)
    except Exception as e:
        logging.error(f"An error occurred during login: {e}")
        logging.error(traceback.format_exc())
        raise

@user_routes.route("/callback", methods=["GET"], endpoint="callback")
def callback():
    try:
        # Handle the authorization code returned by Keycloak
        code = request.args.get("code")
        if not code:
            flash("Authorization code not found.", "danger")
            return redirect(url_for("user_routes.login"))

        # Exchange the authorization code for tokens
        token = keycloak_openid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=url_for("user_routes.callback", _external=True)
        )

        # Store the access token in the session
        session["access_token"] = token["access_token"]
        flash("Logged in successfully!", "success")

        # Redirect to the dashboard
        return redirect(url_for("account_routes.dashboard"))
    except Exception as e:
        logging.error(f"An error occurred during callback: {e}")
        logging.error(traceback.format_exc())
        raise
