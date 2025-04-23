from django.db import models
from django.conf import settings
import uuid

class Account(models.Model):
    """
    Model representing a bank account.
    """
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('investment', 'Investment Account'),
        ('crypto', 'Cryptocurrency Account'),
    )
    
    account_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency_code = models.CharField(max_length=3, default='USD')
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'account'  # Match Flask SQLAlchemy table name
        
    def __str__(self):
        return f"{self.account_type.capitalize()} Account ({self.account_id})"
        
    def deposit(self, amount):
        """Add funds to the account."""
        self.balance += amount
        self.save()
        
    def withdraw(self, amount):
        """Remove funds from the account if sufficient balance."""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
        
    def transfer(self, to_account, amount):
        """Transfer funds from this account to another if sufficient balance."""
        if self.withdraw(amount):
            to_account.deposit(amount)
            return True
        return False
