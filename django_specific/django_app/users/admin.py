from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register the custom User model with the Django admin
admin.site.register(User, UserAdmin)
