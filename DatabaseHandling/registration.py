from werkzeug.security import generate_password_hash
from app_factory import db
from models import User
from extensions import db, bcrypt

def register_user(username, email, password):

    user = User.query.filter_by(email=email).first()
    if user:
        return False

    # Generate the hashed password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Create a new User instance using the provided username and hashed password
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    # Add the new User instance to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()
    
    return new_user
