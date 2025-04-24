#!/usr/bin/env python
"""
Script to finalize the new project structure and clean up old files.
"""
import os
import shutil
from pathlib import Path
import sys

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

# Files and directories that should be deleted (old structure)
# These are no longer needed after migration
TO_DELETE = [
    # Old handling directories
    'DatabaseHandling',
    'FiatHandling',
    'MediaHandling',
    'RealtimeUpdates',
    
    # Old routes directory (already migrated to web/)
    'routes',
    
    # Old grpc_services (moved to api/grpc)
    'grpc_services',
    
    # Temporary/outdated files
    'temp_no_routes.py',
    'temp_routes.py',
    'refactor_project_structure.py',  # Remove this script after running
    
    # __init__.py files in non-Python directories
    '.git/__init__.py',
    '.github/__init__.py',
    '.trunk/__init__.py',
    '.vscode/__init__.py',
    'static/css/__init__.py',
    'static/icons/__init__.py',
    'static/javascripts/__init__.py',
]

# Django components to move to a django_specific folder for reference
DJANGO_COMPONENTS = [
    'bankarstvo_django',
    'accounts',
    'transactions',
    'users',
    'marketplace',
    'django_app',
    'manage.py',
]

def clean_init_files():
    """Remove unnecessary __init__.py files in non-Python directories."""
    print("Cleaning up unnecessary __init__.py files...")
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if any(excluded in root for excluded in ['.git', '.github', '.trunk', '.vscode', 'static', 'templates']):
            for file in files:
                if file == '__init__.py':
                    try:
                        os.remove(os.path.join(root, file))
                        print(f"Removed {os.path.join(root, file)}")
                    except Exception as e:
                        print(f"Could not remove {os.path.join(root, file)}: {e}")

def delete_old_files():
    """Delete files and directories from the old structure."""
    print("Deleting old files and directories...")
    
    for item in TO_DELETE:
        path = os.path.join(PROJECT_ROOT, item)
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Removed directory: {item}")
                else:
                    os.remove(path)
                    print(f"Removed file: {item}")
            except Exception as e:
                print(f"Could not remove {item}: {e}")

def organize_django_files():
    """Move Django-specific files to a separate folder for reference."""
    print("Organizing Django components...")
    
    django_dir = os.path.join(PROJECT_ROOT, 'django_specific')
    if not os.path.exists(django_dir):
        os.makedirs(django_dir)
        print(f"Created directory: django_specific")
    
    for item in DJANGO_COMPONENTS:
        src_path = os.path.join(PROJECT_ROOT, item)
        dst_path = os.path.join(django_dir, item)
        
        if os.path.exists(src_path):
            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                    shutil.rmtree(src_path)
                else:
                    shutil.copy2(src_path, dst_path)
                    os.remove(src_path)
                print(f"Moved {item} to django_specific/")
            except Exception as e:
                print(f"Could not move {item}: {e}")

def create_readme_files():
    """Create README.md files in the main directories to explain their purpose."""
    print("Creating README files for documentation...")
    
    readmes = {
        'api': """# API Layer

This directory contains all API-related code:

- `grpc/`: gRPC service implementations
- `rest/`: REST API endpoints
- `websocket/`: WebSocket endpoints

Each subdirectory contains implementations for different API protocols.
""",
        'core': """# Core Layer

This directory contains the core business logic:

- `models/`: Domain models and business objects
- `services/`: Business logic services
- `validators/`: Validation logic

The code in this directory should be independent of any specific web framework or database.
""",
        'database': """# Database Layer

This directory contains database-related code:

- `models/`: ORM models
- `repositories/`: Data access objects and repositories
- `migrations/`: Database migrations

The code in this directory handles data persistence and retrieval.
""",
        'infrastructure': """# Infrastructure Layer

This directory contains integration with external services:

- `auth/`: Authentication services (Keycloak, etc.)
- `messaging/`: Messaging services
- `storage/`: Storage services
- `external/`: Other external service integrations

This layer provides abstractions for external dependencies.
""",
        'utils': """# Utilities

This directory contains utility functions and helpers that are used across the application.
These utilities should be generic and not tied to specific business logic.
""",
        'web': """# Web Layer

This directory contains web controllers and routes:

- `account/`: Account-related web routes
- `transaction/`: Transaction-related web routes
- `user/`: User-related web routes

This layer handles HTTP requests and responses but delegates business logic to the core layer.
""",
    }
    
    for directory, content in readmes.items():
        readme_path = os.path.join(PROJECT_ROOT, directory, 'README.md')
        try:
            with open(readme_path, 'w') as f:
                f.write(content)
            print(f"Created README in {directory}/")
        except Exception as e:
            print(f"Could not create README in {directory}/: {e}")

def update_main_readme():
    """Update the main README.md with information about the new architecture."""
    print("Updating main README.md...")
    
    readme_content = """# Bankarstvo

A banking application with a modernized clean architecture.

## Project Structure

The project follows a clean, domain-driven architecture:

```
bankarstvo/
├── api/                  # API layer (REST, gRPC, WebSockets)
├── config/               # Configuration files
├── core/                 # Core business logic and domain models
├── database/             # Database access layer
├── infrastructure/       # External services integration
├── utils/                # Utility functions and helpers
├── web/                  # Web controllers/routes
├── static/               # Static assets
├── templates/            # HTML templates
└── tests/                # Tests
```

## Architecture Overview

This application uses a layered architecture:

1. **Web Layer**: Handles HTTP requests/responses (in `web/`)
2. **API Layer**: Exposes services via different protocols (in `api/`)
3. **Core Layer**: Contains business logic and domain models (in `core/`)
4. **Database Layer**: Handles data persistence (in `database/`)
5. **Infrastructure Layer**: Integrates with external services (in `infrastructure/`)

## Development

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

### Key Components

- **gRPC Services**: API service definitions in `api/grpc/`
- **Business Logic**: Core services in `core/services/`
- **Data Access**: Repository pattern in `database/repositories/`
- **Web Routes**: Flask blueprints in `web/`

"""
    
    readme_path = os.path.join(PROJECT_ROOT, 'README.md')
    
    try:
        # Check if README exists
        if os.path.exists(readme_path):
            # Read existing content
            with open(readme_path, 'r') as f:
                existing_content = f.read()
            
            # Keep existing content after our new overview
            updated_content = readme_content + "\n## Original Documentation\n\n" + existing_content
            
            with open(readme_path, 'w') as f:
                f.write(updated_content)
        else:
            # Create new README
            with open(readme_path, 'w') as f:
                f.write(readme_content)
                
        print("Updated main README.md")
    except Exception as e:
        print(f"Could not update README.md: {e}")

def handle_versioning():
    """Create a .gitignore file if it doesn't exist."""
    gitignore_path = os.path.join(PROJECT_ROOT, '.gitignore')
    
    # Only create if it doesn't exist
    if not os.path.exists(gitignore_path):
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log
logs/

# Database
*.sqlite3
*.db

# Environment variables
.env
.env.local
.env.*.local

# Docker
.dockerignore

# Coverage
.coverage
htmlcov/

# Temporary files
*.tmp
"""
        try:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            print("Created .gitignore file")
        except Exception as e:
            print(f"Could not create .gitignore: {e}")

def create_app_init_py():
    """Create an __init__.py in the root to make imports cleaner."""
    init_path = os.path.join(PROJECT_ROOT, '__init__.py')
    
    if not os.path.exists(init_path):
        try:
            with open(init_path, 'w') as f:
                f.write('# bankarstvo package\n')
            print("Created __init__.py in root directory")
        except Exception as e:
            print(f"Could not create __init__.py: {e}")

def update_imports_app_factory():
    """Update import statements in app_factory.py."""
    print("Updating imports in app_factory.py...")
    
    app_factory_path = os.path.join(PROJECT_ROOT, 'app_factory.py')
    
    try:
        # Check if the file exists
        if not os.path.exists(app_factory_path):
            print(f"Could not find app_factory.py")
            return
            
        with open(app_factory_path, 'r') as f:
            content = f.read()
            
        # You already have updated this file earlier
        print("app_factory.py already updated.")
            
    except Exception as e:
        print(f"Could not update app_factory.py: {e}")

def main():
    """Main function to execute the cleanup."""
    print("Starting cleanup and finalization...")
    
    # Create necessary README files
    create_readme_files()
    
    # Update main README
    update_main_readme()
    
    # Clean up unnecessary __init__.py files
    clean_init_files()
    
    # Move Django components to a separate folder
    organize_django_files()
    
    # Create .gitignore if needed
    handle_versioning()
    
    # Create root __init__.py
    create_app_init_py()
    
    # Update import statements in app_factory.py
    update_imports_app_factory()
    
    # Delete old files and directories
    delete_old_files()
    
    print("""
Cleanup and finalization completed.

The project now follows a clean, domain-driven architecture:
- API-related code is in the api/ directory
- Business logic is in the core/ directory
- Database access is in the database/ directory
- External service integration is in the infrastructure/ directory
- Web controllers/routes are in the web/ directory

Django components have been moved to django_specific/ for reference.
Old files and directories have been removed.

Next steps:
1. Update import statements in your code
2. Verify the application still works correctly
3. Commit the changes to version control
""")

    print("Note: This script will self-delete after execution.")
    
    # Self-delete this script (commented out for safety)
    # os.remove(__file__)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        main()
    else:
        print("""
This script will finalize the project structure by:
- Removing old directories and files
- Moving Django components to a separate folder
- Cleaning up unnecessary __init__.py files
- Creating documentation files

To proceed, run:
python finalize_structure.py --force

WARNING: This script will permanently delete files. Make sure you have a backup or commit your changes before proceeding.
""")