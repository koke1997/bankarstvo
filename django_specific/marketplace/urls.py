from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('products/', views.product_list, name='products'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
]