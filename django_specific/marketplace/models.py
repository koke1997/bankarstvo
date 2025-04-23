from django.db import models
from django.conf import settings
import uuid

class Product(models.Model):
    """
    Model representing a product in the marketplace.
    """
    PRODUCT_CATEGORIES = (
        ('financial', 'Financial Services'),
        ('insurance', 'Insurance'),
        ('investment', 'Investment Products'),
        ('loan', 'Loan Products'),
        ('other', 'Other Products'),
    )
    
    product_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=PRODUCT_CATEGORIES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    
    class Meta:
        db_table = 'product'  # Match Flask SQLAlchemy table name
        
    def __str__(self):
        return self.name

class Order(models.Model):
    """
    Model representing an order in the marketplace.
    """
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    order_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    reference_transaction = models.ForeignKey('transactions.Transaction', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'order'  # Match Flask SQLAlchemy table name
        
    def __str__(self):
        return f"Order {self.order_id}"

class OrderItem(models.Model):
    """
    Model representing an item in an order.
    """
    item_id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'  # Match Flask SQLAlchemy table name
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
        
    @property
    def subtotal(self):
        """Calculate subtotal for this order item."""
        return self.price * self.quantity
