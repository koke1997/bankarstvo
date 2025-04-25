from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    keycloak_id = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, username, email, keycloak_id):
        self.username = username
        self.email = email
        self.keycloak_id = keycloak_id

    @staticmethod
    def from_keycloak(keycloak_user):
        """Create a User instance from a Keycloak user object."""
        return User(
            username=keycloak_user.get('username'),
            email=keycloak_user.get('email'),
            keycloak_id=keycloak_user.get('id')
        )

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, keycloak_id={self.keycloak_id})>"