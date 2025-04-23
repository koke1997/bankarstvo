from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('keycloak-callback/', views.keycloak_callback, name='keycloak_callback'),
    path('two-factor/', views.two_factor_auth, name='two_factor'),
]