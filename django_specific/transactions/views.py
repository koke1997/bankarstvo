from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .models import Transaction
from accounts.models import Account
import logging
import decimal

logger = logging.getLogger(__name__)

@login_required
def transaction_history(request):
    """
    Display transaction history for the user.
    """
    user = request.user
    
    # Get all transactions for the user
    transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date_posted')
    
    return render(request, 'transaction_history.html', {
        'transactions': transactions
    })

@login_required
def deposit(request):
    """
    Handle deposit transactions.
    """
    user = request.user
    accounts = Account.objects.filter(user=user)
    
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description', 'Deposit')
        
        try:
            # Convert amount to decimal
            amount_decimal = decimal.Decimal(amount)
            
            # Get the account
            account = get_object_or_404(Account, account_id=account_id, user=user)
            
            # Create transaction and update account balance within a transaction
            with transaction.atomic():
                # Create transaction record
                Transaction.objects.create(
                    user=user,
                    transaction_type='deposit',
                    amount=amount_decimal,
                    description=description,
                    account=account
                )
                
                # Update account balance
                account.balance += amount_decimal
                account.save()
            
            return redirect('accounts:dashboard')
        
        except (ValueError, decimal.InvalidOperation):
            return render(request, 'deposit.html', {
                'accounts': accounts,
                'error': 'Invalid amount'
            })
    
    return render(request, 'deposit.html', {
        'accounts': accounts
    })

@login_required
def withdraw(request):
    """
    Handle withdrawal transactions.
    """
    user = request.user
    accounts = Account.objects.filter(user=user)
    
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description', 'Withdrawal')
        
        try:
            # Convert amount to decimal
            amount_decimal = decimal.Decimal(amount)
            
            # Get the account
            account = get_object_or_404(Account, account_id=account_id, user=user)
            
            # Check if the account has sufficient funds
            if account.balance < amount_decimal:
                return render(request, 'withdraw.html', {
                    'accounts': accounts,
                    'error': 'Insufficient funds'
                })
            
            # Create transaction and update account balance within a transaction
            with transaction.atomic():
                # Create transaction record
                Transaction.objects.create(
                    user=user,
                    transaction_type='withdrawal',
                    amount=amount_decimal,
                    description=description,
                    account=account
                )
                
                # Update account balance
                account.balance -= amount_decimal
                account.save()
            
            return redirect('accounts:dashboard')
        
        except (ValueError, decimal.InvalidOperation):
            return render(request, 'withdraw.html', {
                'accounts': accounts,
                'error': 'Invalid amount'
            })
    
    return render(request, 'withdraw.html', {
        'accounts': accounts
    })

@login_required
def transfer(request):
    """
    Handle transfer transactions between accounts.
    """
    user = request.user
    accounts = Account.objects.filter(user=user)
    
    if request.method == 'POST':
        from_account_id = request.POST.get('from_account_id')
        to_account_id = request.POST.get('to_account_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description', 'Transfer')
        
        try:
            # Convert amount to decimal
            amount_decimal = decimal.Decimal(amount)
            
            # Get the accounts
            from_account = get_object_or_404(Account, account_id=from_account_id, user=user)
            to_account = get_object_or_404(Account, account_id=to_account_id)
            
            # Check if transferring to same account
            if from_account.account_id == to_account.account_id:
                return render(request, 'transfer.html', {
                    'accounts': accounts,
                    'error': 'Cannot transfer to the same account'
                })
            
            # Check if the account has sufficient funds
            if from_account.balance < amount_decimal:
                return render(request, 'transfer.html', {
                    'accounts': accounts,
                    'error': 'Insufficient funds'
                })
            
            # Create transaction and update account balances within a transaction
            with transaction.atomic():
                # Create transaction records
                Transaction.objects.create(
                    user=user,
                    transaction_type='transfer_out',
                    amount=amount_decimal,
                    description=f"{description} - To Account: {to_account.account_id}",
                    account=from_account
                )
                
                Transaction.objects.create(
                    user=to_account.user,
                    transaction_type='transfer_in',
                    amount=amount_decimal,
                    description=f"{description} - From Account: {from_account.account_id}",
                    account=to_account
                )
                
                # Update account balances
                from_account.balance -= amount_decimal
                from_account.save()
                
                to_account.balance += amount_decimal
                to_account.save()
            
            return redirect('accounts:dashboard')
        
        except (ValueError, decimal.InvalidOperation):
            return render(request, 'transfer.html', {
                'accounts': accounts,
                'error': 'Invalid amount'
            })
    
    return render(request, 'transfer.html', {
        'accounts': accounts
    })

@login_required
def crypto_transactions(request):
    """
    Handle cryptocurrency transactions.
    """
    # This is a placeholder for crypto transactions implementation
    return render(request, 'crypto_transactions.html')

@login_required
def stock_transactions(request):
    """
    Handle stock transactions.
    """
    # This is a placeholder for stock transactions implementation
    return render(request, 'stock_transactions.html')
