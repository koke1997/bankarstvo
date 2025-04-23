from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Account, Loan, Payment
from transactions.models import Transaction
from .forms import AccountCreationForm

@login_required
def dashboard(request):
    """
    User dashboard showing account overview and recent transactions.
    """
    # Get all user accounts
    accounts = Account.objects.filter(user=request.user)
    
    # Get recent transactions for all accounts
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date_posted')[:10]
    
    # Get total balance across all accounts
    total_balance = sum(account.balance or 0 for account in accounts)
    
    context = {
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'total_balance': total_balance,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def create_account(request):
    """
    Handle account creation.
    """
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.balance = 0.00  # Start with zero balance
            account.save()
            
            messages.success(request, f'Account {account.account_type} in {account.currency_code} created successfully!')
            return redirect('accounts:dashboard')
    else:
        form = AccountCreationForm()
    
    return render(request, 'create_account.html', {'form': form})

@login_required
def account_details(request, account_id):
    """
    Show detailed information for a specific account.
    """
    account = get_object_or_404(Account, account_id=account_id, user=request.user)
    
    # Get transactions for this account
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date_posted')[:20]
    
    # Calculate statistics
    # Get transactions from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        date_posted__gte=thirty_days_ago
    )
    
    # Calculate income (deposits)
    total_income = sum(t.amount for t in recent_transactions if t.type == 'deposit')
    
    # Calculate expenses (withdrawals)
    total_expenses = sum(t.amount for t in recent_transactions if t.type == 'withdraw')
    
    context = {
        'account': account,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
    }
    
    return render(request, 'account_details.html', context)

@login_required
def account_statement(request, account_id):
    """
    Generate account statement for a specific period.
    """
    account = get_object_or_404(Account, account_id=account_id, user=request.user)
    
    # Default to last 30 days if not specified
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))
    
    # Convert to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get transactions within date range
    transactions = Transaction.objects.filter(
        user=request.user,
        date_posted__gte=start_date,
        date_posted__lte=end_date
    ).order_by('-date_posted')
    
    # Calculate statement statistics
    opening_balance = account.balance - sum(
        t.amount if t.type == 'deposit' else -t.amount 
        for t in transactions
    )
    
    total_deposits = sum(t.amount for t in transactions if t.type == 'deposit')
    total_withdrawals = sum(t.amount for t in transactions if t.type == 'withdraw')
    closing_balance = opening_balance + total_deposits - total_withdrawals
    
    context = {
        'account': account,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
        'opening_balance': opening_balance,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'closing_balance': closing_balance,
    }
    
    return render(request, 'account_statement.html', context)
