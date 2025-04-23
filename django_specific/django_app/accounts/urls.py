from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_account, name='create_account'),
    path('details/<int:account_id>/', views.account_details, name='account_details'),
    path('statement/<int:account_id>/', views.account_statement, name='account_statement'),
]