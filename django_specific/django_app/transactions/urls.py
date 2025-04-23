from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_history, name='history'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path('transfer/', views.transfer, name='transfer'),
    path('crypto/', views.crypto_transactions, name='crypto'),
    path('stocks/', views.stock_transactions, name='stocks'),
]