from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Order, OrderItem
from accounts.models import Account
from transactions.models import Transaction
from django.db import transaction as db_transaction
import logging

logger = logging.getLogger(__name__)

def marketplace_home(request):
    """
    Display the marketplace homepage with featured products.
    """
    # Get featured products (active products, limited to 6)
    featured_products = Product.objects.filter(is_active=True)[:6]
    
    return render(request, 'marketplace_home.html', {
        'featured_products': featured_products
    })

def product_list(request):
    """
    Display a list of all available products.
    """
    # Get category filter from request
    category = request.GET.get('category', '')
    
    # Filter products by category if provided
    if category:
        products = Product.objects.filter(is_active=True, category=category)
    else:
        products = Product.objects.filter(is_active=True)
    
    # Get all available categories for filter dropdown
    categories = Product.PRODUCT_CATEGORIES
    
    return render(request, 'product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category
    })

def product_detail(request, product_id):
    """
    Display details for a specific product.
    """
    product = get_object_or_404(Product, product_id=product_id, is_active=True)
    
    return render(request, 'product_detail.html', {
        'product': product
    })

@login_required
def order_list(request):
    """
    Display a list of orders for the current user.
    """
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-date_created')
    
    return render(request, 'order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    """
    Display details for a specific order.
    """
    user = request.user
    order = get_object_or_404(Order, order_id=order_id, user=user)
    
    # Get all items in this order
    order_items = order.items.all()
    
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items
    })
