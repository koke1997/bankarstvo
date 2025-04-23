from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegistrationForm, UserLoginForm
from .keycloak_manager import KeycloakManager

def index(request):
    """Home view for users app."""
    return render(request, 'index.html')

def login_view(request):
    """
    Handle user login through Django auth or redirect to Keycloak.
    """
    # If Keycloak is enabled, redirect to Keycloak auth
    if not settings.DEBUG and hasattr(settings, 'KEYCLOAK_SERVER_URL'):
        keycloak = KeycloakManager()
        redirect_uri = request.build_absolute_uri(reverse('users:callback'))
        auth_url = keycloak.get_auth_url(redirect_uri)
        return redirect(auth_url)
    
    # Otherwise use Django's authentication
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def callback(request):
    """
    Handle Keycloak callback after successful authentication.
    """
    code = request.GET.get('code')
    if not code:
        return HttpResponse('Authorization code not provided', status=400)
    
    keycloak = KeycloakManager()
    redirect_uri = request.build_absolute_uri(reverse('users:callback'))
    
    # Exchange code for token
    token_data = keycloak.get_token(code, redirect_uri)
    if not token_data:
        return HttpResponse('Failed to get token', status=401)
    
    # Get user info
    access_token = token_data.get('access_token')
    userinfo = keycloak.get_userinfo(access_token)
    if not userinfo:
        return HttpResponse('Failed to get user info', status=401)
    
    # Find or create user
    user = keycloak.find_or_create_user(userinfo)
    
    # Log the user in
    login(request, user)
    
    # Store tokens in session for later use
    request.session['access_token'] = access_token
    request.session['refresh_token'] = token_data.get('refresh_token')
    
    return redirect('accounts:dashboard')

def register(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    """
    User profile view.
    """
    return render(request, 'profile.html')

@login_required
def logout_view(request):
    """
    Handle user logout through Django or Keycloak.
    """
    # If Keycloak was used for login and we have tokens
    if not settings.DEBUG and hasattr(settings, 'KEYCLOAK_SERVER_URL') and request.session.get('access_token'):
        # Clean up Django session
        logout(request)
        
        # Redirect to Keycloak logout
        keycloak = KeycloakManager()
        redirect_uri = request.build_absolute_uri(reverse('users:login'))
        return redirect(keycloak.logout(redirect_uri))
    
    # Otherwise just use Django logout
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('users:login')
