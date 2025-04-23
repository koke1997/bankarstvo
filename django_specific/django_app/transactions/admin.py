from django.contrib import admin
from .models import Transaction, SignedDocument, CryptoAsset, StockAsset

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'type', 'amount', 'date_posted', 'description')
    list_filter = ('type', 'date_posted')
    search_fields = ('user__username', 'description')
    readonly_fields = ('transaction_id', 'date_posted')

@admin.register(SignedDocument)
class SignedDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'user', 'document_type', 'timestamp', 'sender', 'receiver')
    list_filter = ('document_type', 'timestamp')
    search_fields = ('user__username', 'sender', 'receiver')
    readonly_fields = ('document_id', 'timestamp')

@admin.register(CryptoAsset)
class CryptoAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'user', 'name', 'symbol', 'balance')
    list_filter = ('name', 'symbol')
    search_fields = ('user__username', 'name', 'symbol')
    readonly_fields = ('asset_id',)

@admin.register(StockAsset)
class StockAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'user', 'name', 'symbol', 'shares')
    list_filter = ('name', 'symbol')
    search_fields = ('user__username', 'name', 'symbol')
    readonly_fields = ('asset_id',)
