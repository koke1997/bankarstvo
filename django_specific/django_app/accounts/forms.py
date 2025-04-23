from django import forms
from .models import Account

class AccountCreationForm(forms.ModelForm):
    """
    Form for creating a new bank account.
    """
    ACCOUNT_TYPES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('investment', 'Investment Account'),
        ('credit', 'Credit Account'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('GBP', 'British Pound (GBP)'),
        ('JPY', 'Japanese Yen (JPY)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CAD', 'Canadian Dollar (CAD)'),
        ('AUD', 'Australian Dollar (AUD)'),
    ]
    
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPES)
    currency_code = forms.ChoiceField(choices=CURRENCY_CHOICES)
    
    class Meta:
        model = Account
        fields = ['account_type', 'currency_code']