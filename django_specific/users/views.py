from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
import logging
import pyotp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Handle user login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if two-factor auth is enabled
            if user.two_factor_auth:
                # Store user ID in session for two-factor authentication
                request.session['two_factor_user_id'] = user.id
                return redirect('users:two_factor')
            
            # If no two-factor, log in directly
            login(request, user)
            
            # Update last login
            user.last_login = datetime.now()
            user.save()
            
            return redirect('accounts:dashboard')
        else:
            # Authentication failed
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'login.html')

def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect('users:login')

def register(request):
    """
    Handle user registration.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken'})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered'})
        
        # Create new user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            account_created=datetime.now()
        )
        
        # Log in the user
        login(request, user)
        
        return redirect('accounts:dashboard')
    
    return render(request, 'register.html')

@login_required
def profile(request):
    """
    Display and update user profile.
    """
    user = request.user
    
    if request.method == 'POST':
        # Update user profile information
        email = request.POST.get('email')
        
        # Enable/disable two-factor authentication
        two_factor = request.POST.get('two_factor') == 'on'
        
        # If enabling two-factor, generate secret
        if two_factor and not user.two_factor_auth:
            # Generate secret
            secret = pyotp.random_base32()
            user.two_factor_auth_secret = secret
            user.two_factor_auth = True
            user.save()
            
            # Display QR code and setup instructions
            return render(request, 'two_factor_setup.html', {
                'secret': secret,
                'qrcode_url': f"otpauth://totp/Banking:{user.username}?secret={secret}&issuer=BankingApp"
            })
        
        # Update user fields
        user.email = email
        user.two_factor_auth = two_factor
        user.save()
        
        return redirect('users:profile')
    
    return render(request, 'profile.html', {'user': user})

def two_factor_auth(request):
    """
    Handle two-factor authentication.
    """
    if 'two_factor_user_id' not in request.session:
        return redirect('users:login')
    
    if request.method == 'POST':
        # Get the code entered by the user
        code = request.POST.get('code')
        
        # Get the user from the session
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=request.session['two_factor_user_id'])
        except User.DoesNotExist:
            return redirect('users:login')
        
        # Verify the code
        totp = pyotp.TOTP(user.two_factor_auth_secret)
        if totp.verify(code):
            # Log in the user
            login(request, user)
            
            # Update last login
            user.last_login = datetime.now()
            user.save()
            
            # Clear session data
            del request.session['two_factor_user_id']
            
            return redirect('accounts:dashboard')
        else:
            return render(request, 'two_factor.html', {'error': 'Invalid code'})
    
    return render(request, 'two_factor.html')

def keycloak_callback(request):
    """
    Handle callback from Keycloak authentication.
    """
    # This is a placeholder for Keycloak integration
    code = request.GET.get('code')
    
    if code:
        # Process Keycloak authentication code
        # This would involve exchanging the code for tokens
        # and authenticating the user in Django
        
        # For now, just redirect to login
        return redirect('users:login')
    
    return redirect('users:login')
