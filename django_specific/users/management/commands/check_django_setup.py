from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
import os
import sys
import importlib

class Command(BaseCommand):
    """
    A management command to verify that the Django migration is set up correctly.
    This checks various aspects of the installation including database connection,
    template directories, installed apps, and more.
    """
    
    help = "Verifies that your Django migration is set up correctly"
    
    def handle(self, *args, **options):
        self.stdout.write("Starting Django migration health check...")
        
        # Check 1: Verify database connection
        self.stdout.write("Checking database connection...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                if row[0] == 1:
                    self.stdout.write(self.style.SUCCESS("✓ Database connection successful"))
                else:
                    self.stdout.write(self.style.ERROR("✗ Database query returned unexpected result"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Database connection failed: {e}"))
        
        # Check 2: Verify template directories
        self.stdout.write("Checking template directories...")
        template_dirs = settings.TEMPLATES[0]['DIRS']
        if template_dirs:
            for template_dir in template_dirs:
                if os.path.exists(template_dir):
                    self.stdout.write(self.style.SUCCESS(f"✓ Template directory exists: {template_dir}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Template directory does not exist: {template_dir}"))
        else:
            self.stdout.write(self.style.WARNING("! No template directories are explicitly configured"))
        
        # Check 3: Verify static files
        self.stdout.write("Checking static files configuration...")
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            self.stdout.write(self.style.SUCCESS(f"✓ STATIC_ROOT is configured: {settings.STATIC_ROOT}"))
        else:
            self.stdout.write(self.style.WARNING("! STATIC_ROOT is not configured"))
            
        if hasattr(settings, 'STATICFILES_DIRS'):
            for static_dir in settings.STATICFILES_DIRS:
                if os.path.exists(static_dir):
                    self.stdout.write(self.style.SUCCESS(f"✓ Static directory exists: {static_dir}"))
                else:
                    self.stdout.write(self.style.ERROR(f"✗ Static directory does not exist: {static_dir}"))
        
        # Check 4: Verify installed apps
        self.stdout.write("Checking installed apps...")
        required_apps = ['accounts', 'users', 'transactions', 'marketplace']
        
        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                # Try to import the models from the app
                try:
                    models_module = importlib.import_module(f"{app}.models")
                    self.stdout.write(self.style.SUCCESS(f"✓ App '{app}' is installed and models can be imported"))
                except ImportError as e:
                    self.stdout.write(self.style.ERROR(f"✗ App '{app}' is installed but models cannot be imported: {e}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Required app '{app}' is not installed"))
        
        # Check 5: Verify URL configurations
        self.stdout.write("Checking URL configurations...")
        for app in required_apps:
            try:
                urls_module = importlib.import_module(f"{app}.urls")
                self.stdout.write(self.style.SUCCESS(f"✓ URL configuration for '{app}' can be imported"))
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f"✗ URL configuration for '{app}' cannot be imported: {e}"))
        
        # Final report
        self.stdout.write("Django migration health check complete.")
        self.stdout.write("To run the Django application, use: python manage.py runserver")
        self.stdout.write("For Docker, use: docker-compose -f docker-compose-hybrid.yml up -d")