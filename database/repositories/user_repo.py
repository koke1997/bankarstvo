from werkzeug.security import generate_password_hash
from app_factory import db
from core.models import User
from utils.extensions import db, bcrypt
import pyotp

def register_user(username, email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        return False

    # Generate the hashed password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Generate a new multi-factor authentication secret
    mfa_secret = pyotp.random_base32()

    # Create a new User instance using the provided username, hashed password, and MFA secret
    new_user = User(username=username, email=email, password_hash=hashed_password, two_factor_auth_secret=mfa_secret)

    # Add the new User instance to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()

    return new_user
