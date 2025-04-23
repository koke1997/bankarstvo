"""
ASGI config for bankarstvo_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bankarstvo_django.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import after initializing Django
from django.urls import path
from accounts.consumers import NotificationsConsumer

# Define WebSocket URL patterns
websocket_urlpatterns = [
    path('ws/notifications/', NotificationsConsumer.as_asgi()),
]

# Configure the ASGI application with both HTTP and WebSocket support
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
