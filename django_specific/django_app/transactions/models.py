from django.db import models
from django.utils import timezone
from users.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    date_posted = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    description = models.CharField(max_length=100, null=True, blank=True)
    amount = models.FloatField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    
    def __str__(self):
        return f"{self.type.capitalize()} of {self.amount} on {self.date_posted.strftime('%Y-%m-%d')}"
    
    class Meta:
        db_table = 'transactions'  # Match the existing table name
        ordering = ['-date_posted']

class SignedDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='signed_documents', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    document_type = models.CharField(max_length=255, null=True, blank=True)
    additional_info = models.TextField(null=True, blank=True)
    sender = models.CharField(max_length=255)
    receiver = models.CharField(max_length=255)
    image_data = models.TextField()  # Stores the base64 image
    
    def __str__(self):
        return f"Document {self.document_id} ({self.document_type}) - {self.timestamp.strftime('%Y-%m-%d')}"
    
    class Meta:
        db_table = 'signed_documents'  # Match the existing table name

class CryptoAsset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_assets')
    balance = models.DecimalField(max_digits=20, decimal_places=8)
    
    def __str__(self):
        return f"{self.name} ({self.symbol}): {self.balance}"
    
    class Meta:
        db_table = 'crypto_assets'  # Match the existing table name
        unique_together = ['user', 'symbol']

class StockAsset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_assets')
    shares = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.symbol}): {self.shares} shares"
    
    class Meta:
        db_table = 'stock_assets'  # Match the existing table name
        unique_together = ['user', 'symbol']
