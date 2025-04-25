# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
import pyotp
from flask import request, jsonify
from functools import wraps
import jwt  # Replace 'from jwt import *' with 'import jwt'
import requests
import os

logger = logging.getLogger(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Removed redundant db.init_app(app) call
def create_extensions(app):
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        logging.info(f"Loading user with ID {user_id}")
        from database.models.user import User  # Import User from the correct module
        user = User.query.get(int(user_id))
        logging.info(f"Loaded user: {user}")
        return user

# Middleware to validate JWT tokens
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        
        # Skip token validation in test mode
        if current_app.config.get("TESTING") or current_app.config.get("SKIP_KEYCLOAK"):
            logger.info("Skipping token validation in test mode")
            return f(*args, **kwargs)
            
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Remove 'Bearer ' prefix if present
            token = token.split()[1] if " " in token else token

            # Fetch Keycloak public key
            keycloak_url = f"{os.getenv('KEYCLOAK_AUTH_SERVER_URL')}/realms/{os.getenv('KEYCLOAK_REALM')}/protocol/openid-connect/certs"
            public_key = requests.get(keycloak_url).json()["keys"][0]["x5c"][0]
            public_key = f"-----BEGIN CERTIFICATE-----\n{public_key}\n-----END CERTIFICATE-----"

            # Decode and validate the token
            decoded_token = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=os.getenv("KEYCLOAK_RESOURCE"),
                issuer=f"{os.getenv('KEYCLOAK_AUTH_SERVER_URL')}/realms/{os.getenv('KEYCLOAK_REALM')}"
            )

            # Add token claims to the request context
            request.token_claims = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return jsonify({"message": "Token validation failed!"}), 401

        return f(*args, **kwargs)

    return decorated

# models.py should be imported after the extensions are defined
from core.models import User
