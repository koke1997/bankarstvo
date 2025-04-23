from django.db import models
from django.utils import timezone
from users.models import User

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    account_type = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    currency_code = models.CharField(max_length=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    
    def __str__(self):
        return f"Account {self.account_id}: {self.account_type} ({self.currency_code})"
    
    class Meta:
        db_table = 'accounts'  # Match the existing table name

class Loan(models.Model):
    LOAN_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('defaulted', 'Defaulted'),
        ('pending', 'Pending Approval'),
    ]
    
    loan_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    interest_rate = models.FloatField()
    term = models.IntegerField()  # Term in months
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=LOAN_STATUS_CHOICES, default='active')
    
    def __str__(self):
        return f"Loan {self.loan_id}: {self.amount} at {self.interest_rate}% for {self.term} months"
    
    class Meta:
        db_table = 'loans'  # Match the existing table name

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='completed')
    
    def __str__(self):
        return f"Payment {self.payment_id}: {self.amount} on {self.payment_date}"
    
    class Meta:
        db_table = 'payments'  # Match the existing table name
