from django import forms
from accounts.models import Account
from .models import Transaction

class DepositForm(forms.Form):
    """Form for processing a deposit."""
    account = forms.ModelChoiceField(queryset=None)
    amount = forms.DecimalField(min_value=0.01, decimal_places=2)
    description = forms.CharField(max_length=100, required=False)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DepositForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            
class WithdrawForm(forms.Form):
    """Form for processing a withdrawal."""
    account = forms.ModelChoiceField(queryset=None)
    amount = forms.DecimalField(min_value=0.01, decimal_places=2)
    description = forms.CharField(max_length=100, required=False)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(WithdrawForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
    
    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        amount = cleaned_data.get('amount')
        
        if account and amount:
            if account.balance is None or account.balance < amount:
                raise forms.ValidationError(f"Insufficient funds in {account.account_type} account. Available balance: {account.balance or 0}")
        
        return cleaned_data

class TransferForm(forms.Form):
    """Form for processing a transfer between accounts."""
    from_account = forms.ModelChoiceField(queryset=None)
    to_account = forms.ModelChoiceField(queryset=None)
    amount = forms.DecimalField(min_value=0.01, decimal_places=2)
    description = forms.CharField(max_length=100, required=False)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransferForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['from_account'].queryset = Account.objects.filter(user=user)
            self.fields['to_account'].queryset = Account.objects.filter(user=user)
    
    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        amount = cleaned_data.get('amount')
        
        if from_account and to_account and amount:
            # Check if accounts are the same
            if from_account == to_account:
                raise forms.ValidationError("Cannot transfer to the same account")
            
            # Check if sufficient funds
            if from_account.balance is None or from_account.balance < amount:
                raise forms.ValidationError(f"Insufficient funds in {from_account.account_type} account. Available balance: {from_account.balance or 0}")
        
        return cleaned_data