from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Account
from transactions.models import Transaction
import logging

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    """
    Display the user's dashboard with account information.
    """
    user = request.user
    accounts = Account.objects.filter(user=user)
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date_posted')[:5]
    
    context = {
        'accounts': accounts,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def create_account(request):
    """
    Handle account creation.
    """
    if request.method == 'POST':
        account_type = request.POST.get('account_type')
        currency_code = request.POST.get('currency_code', 'USD')
        
        # Create a new account
        account = Account.objects.create(
            user=request.user,
            account_type=account_type,
            currency_code=currency_code,
            balance=0.00
        )
        
        return redirect('accounts:dashboard')
    
    return render(request, 'create_account.html')

@login_required
def account_details(request, account_id):
    """
    Display account details.
    """
    account = get_object_or_404(Account, account_id=account_id, user=request.user)
    
    # Get transactions for this account
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date_posted')[:10]
    
    context = {
        'account': account,
        'transactions': transactions,
    }
    
    return render(request, 'account_details.html', context)

@login_required
def account_statement(request, account_id):
    """
    Generate account statement.
    """
    account = get_object_or_404(Account, account_id=account_id, user=request.user)
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Get transactions for this account within date range
    transactions_query = Transaction.objects.filter(user=request.user)
    
    if start_date:
        transactions_query = transactions_query.filter(date_posted__gte=start_date)
    
    if end_date:
        transactions_query = transactions_query.filter(date_posted__lte=end_date)
    
    transactions = transactions_query.order_by('-date_posted')
    
    context = {
        'account': account,
        'transactions': transactions,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'account_statement.html', context)
