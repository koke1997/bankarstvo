# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
import pyotp

logger = logging.getLogger(__name__)

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_extensions(app):
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        logging.info(f"Loading user with ID {user_id}")
        user = User.query.get(int(user_id))
        logging.info(f"Loaded user: {user}")
        return user

# models.py should be imported after the extensions are defined
from core.models import User
