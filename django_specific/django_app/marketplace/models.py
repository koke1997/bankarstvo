from django.db import models
from django.utils import timezone
from users.models import User

class MarketplaceItem(models.Model):
    ITEM_STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
    ]
    
    item_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='selling_items')
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='purchased_items', null=True, blank=True)
    status = models.CharField(max_length=50, choices=ITEM_STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}: {self.price} ({self.status})"
    
    class Meta:
        db_table = 'marketplace_items'  # Match the existing table name

class MarketplaceTransaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='transactions')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_sales')
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    
    def __str__(self):
        return f"Transaction {self.transaction_id}: {self.item.name} sold for {self.amount}"
    
    class Meta:
        db_table = 'marketplace_transactions'  # Match the existing table name
