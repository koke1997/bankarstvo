from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from decimal import Decimal

from .models import MarketplaceItem, MarketplaceTransaction
from accounts.models import Account
from .forms import ListItemForm, PurchaseItemForm

@login_required
def marketplace_home(request):
    """Home page for the marketplace."""
    items = MarketplaceItem.objects.filter(status='available').exclude(seller=request.user)
    my_listings = MarketplaceItem.objects.filter(seller=request.user)
    
    return render(request, 'marketplace/home.html', {
        'items': items,
        'my_listings': my_listings
    })

@login_required
def product_list(request):
    """View all available marketplace items."""
    items = MarketplaceItem.objects.filter(status='available').exclude(seller=request.user)
    return render(request, 'marketplace/product_list.html', {'items': items})

@login_required
def product_detail(request, product_id):
    """View details of a specific marketplace item and allow purchase."""
    item = get_object_or_404(MarketplaceItem, item_id=product_id)
    
    if request.method == 'POST':
        form = PurchaseItemForm(request.POST, user=request.user)
        if form.is_valid():
            account = form.cleaned_data['account']
            
            # Check if item is still available
            if item.status != 'available':
                messages.error(request, 'This item is no longer available')
                return redirect('marketplace:product_detail', product_id=product_id)
            
            # Check if user has sufficient funds
            if account.balance < item.price:
                messages.error(request, f'Insufficient funds in selected account. Available: {account.balance}')
                return redirect('marketplace:product_detail', product_id=product_id)
            
            # Process the purchase
            with db_transaction.atomic():
                # Update the account balance
                account.balance -= item.price
                account.save()
                
                # Update the item status
                item.status = 'sold'
                item.buyer = request.user
                item.save()
                
                # Create a marketplace transaction record
                MarketplaceTransaction.objects.create(
                    item=item,
                    buyer=request.user,
                    seller=item.seller,
                    amount=item.price
                )
            
            messages.success(request, f'Successfully purchased {item.name} for {item.price}')
            return redirect('marketplace:orders')
    else:
        form = PurchaseItemForm(user=request.user)
    
    return render(request, 'marketplace/product_detail.html', {
        'item': item,
        'form': form
    })

@login_required
def order_list(request):
    """View list of user's marketplace orders."""
    purchases = MarketplaceTransaction.objects.filter(buyer=request.user).order_by('-timestamp')
    sales = MarketplaceTransaction.objects.filter(seller=request.user).order_by('-timestamp')
    
    return render(request, 'marketplace/order_list.html', {
        'purchases': purchases,
        'sales': sales
    })

@login_required
def order_detail(request, order_id):
    """View details of a specific marketplace order."""
    transaction = get_object_or_404(
        MarketplaceTransaction, 
        transaction_id=order_id,
        buyer=request.user
    )
    
    return render(request, 'marketplace/order_detail.html', {
        'transaction': transaction
    })
