from werkzeug.security import generate_password_hash
from utils.extensions import db, bcrypt
import pyotp
from core.models import User

def register_user(username, email, password):
    # Use db.session.query instead of User.query
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        return False

    # Generate the hashed password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Generate a new multi-factor authentication secret
    mfa_secret = pyotp.random_base32()

    # Create a new User instance using the provided username, hashed password, and MFA secret
    new_user = User(
        username=username, 
        email=email, 
        password_hash=hashed_password, 
        two_factor_auth_secret=mfa_secret
    )

    # Add the new User instance to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()

    return new_user

def get_user_by_id(user_id):
    """Get a user by ID."""
    if not user_id:
        return None
    return db.session.query(User).filter_by(user_id=user_id).first()

def get_user_by_email(email):
    """Get a user by email."""
    if not email:
        return None
    return db.session.query(User).filter_by(email=email).first()

def get_user_by_username(username):
    """Get a user by username."""
    if not username:
        return None
    return db.session.query(User).filter_by(username=username).first()

def create_user(username, email, password):
    """Create a new user."""
    # Check if user already exists
    existing_user = db.session.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        if existing_user.username == username:
            raise ValueError("Username already exists")
        else:
            raise ValueError("Email already exists")
    
    # Create new user with proper initialization
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    
    db.session.add(user)
    db.session.commit()
    return user

def update_user(user):
    """Update an existing user."""
    if not user or not isinstance(user, User):
        return False
    
    db.session.commit()
    return True
