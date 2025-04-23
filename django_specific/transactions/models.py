from django.db import models
from django.conf import settings
import uuid

class Transaction(models.Model):
    """
    Model representing a financial transaction.
    """
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('payment', 'Payment'),
        ('fee', 'Fee'),
        ('interest', 'Interest'),
        ('crypto_buy', 'Cryptocurrency Purchase'),
        ('crypto_sell', 'Cryptocurrency Sale'),
        ('stock_buy', 'Stock Purchase'),
        ('stock_sell', 'Stock Sale'),
    )
    
    transaction_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    reference_id = models.CharField(max_length=36, blank=True, null=True)
    
    class Meta:
        db_table = 'transaction'  # Match Flask SQLAlchemy table name
        ordering = ['-date_posted']
        
    def __str__(self):
        return f"{self.transaction_type.capitalize()}: {self.amount} ({self.transaction_id})"
