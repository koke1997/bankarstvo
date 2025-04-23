from django.contrib import admin
from .models import MarketplaceItem, MarketplaceTransaction

@admin.register(MarketplaceItem)
class MarketplaceItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'name', 'price', 'seller', 'buyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'seller__username', 'buyer__username')
    readonly_fields = ('item_id', 'created_at', 'updated_at')

@admin.register(MarketplaceTransaction)
class MarketplaceTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'item', 'buyer', 'seller', 'amount', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('item__name', 'buyer__username', 'seller__username')
    readonly_fields = ('transaction_id', 'timestamp')
