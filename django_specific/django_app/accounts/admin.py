from django.contrib import admin
from .models import Account, Loan, Payment

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'user', 'account_type', 'balance', 'currency_code')
    list_filter = ('account_type', 'currency_code')
    search_fields = ('user__username', 'user__email', 'account_type')
    readonly_fields = ('account_id',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'user', 'amount', 'interest_rate', 'term', 'status')
    list_filter = ('status', 'interest_rate')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('loan_id',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'loan', 'amount', 'payment_date', 'status')
    list_filter = ('status', 'payment_date')
    search_fields = ('loan__user__username',)
    readonly_fields = ('payment_id',)
