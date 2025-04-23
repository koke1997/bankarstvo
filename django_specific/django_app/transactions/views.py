from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Transaction, CryptoAsset, StockAsset
from accounts.models import Account
from .forms import DepositForm, WithdrawForm, TransferForm
from users.models import User

@login_required
def transaction_history(request):
    """View transaction history for a user."""
    transactions = Transaction.objects.filter(user=request.user).order_by('-date_posted')
    return render(request, 'transaction_history.html', {'transactions': transactions})

@login_required
def deposit(request):
    """Handle deposit operation."""
    if request.method == 'POST':
        form = DepositForm(request.POST, user=request.user)
        if form.is_valid():
            # Get form data
            account_id = form.cleaned_data['account'].account_id
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            # Get the account
            account = get_object_or_404(Account, account_id=account_id, user=request.user)
            
            # Create the transaction and update account balance
            with transaction.atomic():
                # Create transaction record
                transaction_record = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    description=description,
                    type='deposit'
                )
                
                # Update account balance
                if account.balance is None:
                    account.balance = 0
                account.balance += Decimal(str(amount))
                account.save()
            
            messages.success(request, f'Successfully deposited {amount} to {account.account_type}')
            return redirect('accounts:dashboard')
    else:
        form = DepositForm(user=request.user)
    
    return render(request, 'deposit.html', {'form': form})

@login_required
def withdraw(request):
    """Handle withdrawal operation."""
    if request.method == 'POST':
        form = WithdrawForm(request.POST, user=request.user)
        if form.is_valid():
            # Get form data
            account_id = form.cleaned_data['account'].account_id
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            # Get the account
            account = get_object_or_404(Account, account_id=account_id, user=request.user)
            
            # Check if sufficient balance
            if account.balance is None or account.balance < Decimal(str(amount)):
                messages.error(request, 'Insufficient balance for withdrawal')
                return redirect('transactions:withdraw')
            
            # Create the transaction and update account balance
            with transaction.atomic():
                # Create transaction record
                transaction_record = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    description=description,
                    type='withdraw'
                )
                
                # Update account balance
                account.balance -= Decimal(str(amount))
                account.save()
            
            messages.success(request, f'Successfully withdrew {amount} from {account.account_type}')
            return redirect('accounts:dashboard')
    else:
        form = WithdrawForm(user=request.user)
    
    return render(request, 'withdraw.html', {'form': form})

@login_required
def transfer(request):
    """Handle transfer between accounts."""
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)
        if form.is_valid():
            # Get form data
            from_account_id = form.cleaned_data['from_account'].account_id
            to_account_id = form.cleaned_data['to_account'].account_id
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            
            # Check if source and destination are different
            if from_account_id == to_account_id:
                messages.error(request, 'Cannot transfer to the same account')
                return redirect('transactions:transfer')
            
            # Get the accounts
            from_account = get_object_or_404(Account, account_id=from_account_id, user=request.user)
            to_account = get_object_or_404(Account, account_id=to_account_id, user=request.user)
            
            # Check if sufficient balance
            if from_account.balance is None or from_account.balance < Decimal(str(amount)):
                messages.error(request, 'Insufficient balance for transfer')
                return redirect('transactions:transfer')
            
            # Create the transaction and update account balances
            with transaction.atomic():
                # Create transaction record
                transaction_record = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    description=description,
                    type='transfer'
                )
                
                # Update account balances
                from_account.balance -= Decimal(str(amount))
                from_account.save()
                
                if to_account.balance is None:
                    to_account.balance = 0
                to_account.balance += Decimal(str(amount))
                to_account.save()
            
            messages.success(
                request, 
                f'Successfully transferred {amount} from {from_account.account_type} to {to_account.account_type}'
            )
            return redirect('accounts:dashboard')
    else:
        form = TransferForm(user=request.user)
    
    return render(request, 'transfer.html', {'form': form})

@login_required
def crypto_transactions(request):
    """View crypto assets and transactions."""
    crypto_assets = CryptoAsset.objects.filter(user=request.user)
    return render(request, 'crypto.html', {'crypto_assets': crypto_assets})

@login_required
def stock_transactions(request):
    """View stock assets and transactions."""
    stock_assets = StockAsset.objects.filter(user=request.user)
    return render(request, 'stocks.html', {'stock_assets': stock_assets})
