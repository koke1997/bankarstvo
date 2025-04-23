from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Extended User model for the banking application.
    Inherits from Django's AbstractUser and adds banking-specific fields.
    """
    two_factor_auth = models.BooleanField(default=False)
    two_factor_auth_code = models.CharField(max_length=255, null=True, blank=True)
    two_factor_auth_expiry = models.DateTimeField(null=True, blank=True)
    two_factor_auth_secret = models.CharField(max_length=255, null=True, blank=True)
    
    account_created = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    class Meta:
        db_table = 'user'  # Match the existing table name
