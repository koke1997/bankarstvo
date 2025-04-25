#!/usr/bin/env python
"""
This script runs scheduled Keycloak synchronization to keep users synchronized
between the local database and Keycloak.

This script can be scheduled with cron (Linux/macOS) or Task Scheduler (Windows)
to run periodically, such as hourly or daily.

Example cron entry (daily at 1am):
0 1 * * * /path/to/python /path/to/scripts/keycloak_sync_scheduled.py >> /path/to/logs/keycloak_sync.log 2>&1

Example Windows Task Scheduler:
Program/script: python.exe
Arguments: C:\path\to\scripts\keycloak_sync_scheduled.py
"""
import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add the project root directory to the Python path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from app_factory import create_app
from infrastructure.auth.user_sync_service import UserSyncService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("keycloak_sync")

def run_sync(direction="both", dry_run=False):
    """
    Run Keycloak synchronization in the specified direction.
    
    Args:
        direction: The synchronization direction ('to_keycloak', 'from_keycloak', or 'both')
        dry_run: If True, don't make any changes, just log what would be done
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    app = create_app()
    
    with app.app_context():
        logger.info(f"Starting Keycloak synchronization ({direction} direction)")
        start_time = datetime.now()
        
        results = []
        
        if direction in ("from_keycloak", "both"):
            # Sync users from Keycloak to the database
            logger.info("Syncing users from Keycloak to database...")
            
            if not dry_run:
                total, success, errors = UserSyncService.sync_all_users_from_keycloak()
                results.append(f"Imported {success}/{total} users from Keycloak ({errors} errors)")
            else:
                logger.info("[DRY RUN] Would sync users from Keycloak to database")
                results.append("[DRY RUN] Would import users from Keycloak")
        
        if direction in ("to_keycloak", "both"):
            # Sync users from the database to Keycloak
            logger.info("Syncing users from database to Keycloak...")
            
            if not dry_run:
                # First, update existing users in Keycloak
                total_updates, success_updates, error_updates = UserSyncService.sync_user_changes_to_keycloak()
                results.append(f"Updated {success_updates}/{total_updates} users in Keycloak ({error_updates} errors)")
                
                # Then, export users that are not in Keycloak yet
                total_new, success_new, error_new = UserSyncService.export_all_users_to_keycloak()
                results.append(f"Exported {success_new}/{total_new} new users to Keycloak ({error_new} errors)")
            else:
                logger.info("[DRY RUN] Would sync users from database to Keycloak")
                results.append("[DRY RUN] Would export users to Keycloak")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = f"Keycloak synchronization completed in {duration:.2f} seconds"
        logger.info(summary)
        for result in results:
            logger.info(result)
        
        return True, summary

def main():
    parser = argparse.ArgumentParser(description="Keycloak user synchronization")
    parser.add_argument(
        "--direction",
        choices=["to_keycloak", "from_keycloak", "both"],
        default="both",
        help="Synchronization direction: to_keycloak, from_keycloak, or both (default)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - don't make any changes, just log what would be done"
    )
    
    args = parser.parse_args()
    
    try:
        success, message = run_sync(direction=args.direction, dry_run=args.dry_run)
        if not success:
            logger.error(f"Synchronization failed: {message}")
            sys.exit(1)
    except Exception as e:
        logger.exception(f"Error running synchronization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()