from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    """
    Custom user model for the banking application.
    Extends Django's AbstractUser to add additional fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    account_created = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Two-factor authentication fields
    two_factor_auth = models.BooleanField(default=False)
    two_factor_auth_secret = models.CharField(max_length=50, blank=True, null=True)
    
    # Keycloak integration fields
    keycloak_id = models.CharField(max_length=36, blank=True, null=True)
    
    # Additional security fields
    login_attempts = models.IntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user'  # Match Flask SQLAlchemy table name
        
    def __str__(self):
        return self.username
    
    def reset_login_attempts(self):
        """Reset login attempts counter."""
        self.login_attempts = 0
        self.save()
    
    def increment_login_attempts(self):
        """Increment login attempts and handle account locking."""
        self.login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.login_attempts >= 5:
            self.account_locked = True
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save()
    
    def update_last_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = timezone.now()
        self.save()
        
    @property
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.account_locked and self.account_locked_until:
            if timezone.now() > self.account_locked_until:
                # Unlock account if lock period has expired
                self.account_locked = False
                self.login_attempts = 0
                self.save()
                return False
            return True
        return False
