import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class KeycloakManager:
    def __init__(self):
        self.server_url = settings.KEYCLOAK_SERVER_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET
        self.base_url = f"{self.server_url}/realms/{self.realm}/protocol/openid-connect"
    
    def get_auth_url(self, redirect_uri):
        """Generate Keycloak authorization URL for login."""
        return f"{self.base_url}/auth?client_id={self.client_id}&response_type=code&redirect_uri={redirect_uri}"
    
    def get_token(self, code, redirect_uri):
        """Exchange authorization code for tokens."""
        url = f"{self.base_url}/token"
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_userinfo(self, access_token):
        """Get user information using the access token."""
        url = f"{self.base_url}/userinfo"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    def find_or_create_user(self, userinfo):
        """Find or create a user based on Keycloak userinfo."""
        # Extract relevant information from userinfo
        email = userinfo.get('email', '')
        username = userinfo.get('preferred_username', '')
        first_name = userinfo.get('given_name', '')
        last_name = userinfo.get('family_name', '')
        
        # Try to find the user by email
        try:
            user = User.objects.get(email=email)
            # Update user info if needed
            if user.username != username or user.first_name != first_name or user.last_name != last_name:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.save()
        except User.DoesNotExist:
            # Create a new user if not found
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
        return user
    
    def logout(self, redirect_uri):
        """Generate Keycloak logout URL."""
        return f"{self.base_url}/logout?client_id={self.client_id}&redirect_uri={redirect_uri}"