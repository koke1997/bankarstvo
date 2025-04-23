# User model
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, **kwargs):
        """
        User model for the application.
        """
        # Initialize attributes with default values
        self.user_id = kwargs.get('user_id', None)
        self.username = kwargs.get('username', '')
        self.email = kwargs.get('email', '')
        self.password_hash = kwargs.get('password_hash', 'temp_hash')
        self.two_factor_auth = kwargs.get('two_factor_auth', False)
        self.two_factor_auth_code = kwargs.get('two_factor_auth_code', None)
        self.two_factor_auth_expiry = kwargs.get('two_factor_auth_expiry', None)
        self.two_factor_auth_secret = kwargs.get('two_factor_auth_secret', None)
        self.account_created = kwargs.get('account_created', datetime.now())
        self.last_login = kwargs.get('last_login', None)
        self.is_active = kwargs.get('is_active', True)
    
    @property
    def id(self):
        """Get the ID of the user."""
        return self.user_id
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
