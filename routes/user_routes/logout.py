import os
from flask import redirect, url_for
from . import user_routes
from DatabaseHandling.authentication import logout_func
from keycloak import KeycloakOpenID
from utils.extensions import token_required

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv("KEYCLOAK_SERVER_URL"),
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    realm_name=os.getenv("KEYCLOAK_REALM_NAME"),
    client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET_KEY")
)

@user_routes.route('/logout', methods=['GET'], endpoint="logout")
@token_required
def logout():
    logout_func()
    keycloak_openid.logout()
    return redirect(url_for('user_routes.login'))
