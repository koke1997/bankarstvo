from django import forms
from accounts.models import Account
from .models import MarketplaceItem

class ListItemForm(forms.ModelForm):
    """Form for listing a new item in the marketplace."""
    class Meta:
        model = MarketplaceItem
        fields = ['name', 'description', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

class PurchaseItemForm(forms.Form):
    """Form for purchasing an item from the marketplace."""
    account = forms.ModelChoiceField(queryset=None, label="Select account for payment")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PurchaseItemForm, self).__init__(*args, **kwargs)
        
        if user:
            # Only show accounts with a positive balance
            self.fields['account'].queryset = Account.objects.filter(user=user).exclude(balance__lte=0)