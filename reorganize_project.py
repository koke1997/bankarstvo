#!/usr/bin/env python
"""
Project Restructuring Script

This script reorganizes the project directory structure by moving files
into more appropriate directories based on their function.
"""

import os
import shutil
import errno

def create_directory(path):
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def move_file(src, dest):
    """Move a file from src to dest, creating parent directories if needed."""
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(src, dest)
        print(f"Moved {src} to {dest}")
    except FileNotFoundError:
        print(f"File not found: {src}")
    except Exception as e:
        print(f"Error moving {src} to {dest}: {e}")

def main():
    # Get project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Create new directories
    print("Creating new directories...")
    create_directory(os.path.join(project_root, "scripts"))
    create_directory(os.path.join(project_root, "deployment"))
    
    # Files to move to scripts/
    script_files = [
        "dev.bat", "dev.sh", "finalize_structure.py",
        "flask_django_manager.bat", "flask_django_manager.sh",
        "cli.py", "debug.py", "start.sh"
    ]
    
    # Files to move to config/
    config_files = [
        "keycloak.json", "postcss.config.js", "tailwind.config.js",
        "tsconfig.json", "webpack.config.js", "pytest.ini"
    ]
    
    # Files to move to deployment/
    deployment_files = [
        "docker-compose-hybrid.yml", "docker-compose.yml",
        "docker-entrypoint.sh", "Dockerfile", 
        "setup.sql", "template_for_database.sql"
    ]
    
    # Files to move to docs/
    doc_files = [
        "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "DEVELOPMENT.md",
        "LICENSE.md", "SECURITY.md"
    ]
    
    # Copy README.md to docs/ (keep in root)
    if os.path.exists(os.path.join(project_root, "README.md")):
        shutil.copy(
            os.path.join(project_root, "README.md"),
            os.path.join(project_root, "docs", "README.md")
        )
        print("Copied README.md to docs/")
    
    # Move files to scripts/
    print("\nMoving script files...")
    for file in script_files:
        src = os.path.join(project_root, file)
        dest = os.path.join(project_root, "scripts", file)
        move_file(src, dest)
    
    # Move files to config/
    print("\nMoving config files...")
    for file in config_files:
        src = os.path.join(project_root, file)
        dest = os.path.join(project_root, "config", file)
        move_file(src, dest)
    
    # Move files to deployment/
    print("\nMoving deployment files...")
    for file in deployment_files:
        src = os.path.join(project_root, file)
        dest = os.path.join(project_root, "deployment", file)
        move_file(src, dest)
    
    # Move files to docs/
    print("\nMoving documentation files...")
    for file in doc_files:
        src = os.path.join(project_root, file)
        dest = os.path.join(project_root, "docs", file)
        move_file(src, dest)
    
    print("\nProject restructuring complete!")
    print("Remember to update imports and file references in your code.")

if __name__ == "__main__":
    main()