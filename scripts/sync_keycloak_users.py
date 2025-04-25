"""
Command-line script to synchronize users between Keycloak and the database
"""
import os
import sys
import logging
import traceback
from argparse import ArgumentParser

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_parser():
    """Set up the command-line argument parser"""
    parser = ArgumentParser(description='Synchronize users between Keycloak and database')
    parser.add_argument('--direction', choices=['import', 'export', 'both'], default='both',
                        help='Direction of synchronization: import (Keycloak->DB), export (DB->Keycloak), or both')
    parser.add_argument('--username', type=str, help='Sync only a specific username')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    return parser

def import_from_keycloak(app, username=None, dry_run=False):
    """Import users from Keycloak to the database"""
    from infrastructure.auth.user_sync_service import UserSyncService
    
    if username:
        logger.info(f"Importing user '{username}' from Keycloak to database")
        if dry_run:
            logger.info(f"[DRY RUN] Would import user '{username}' from Keycloak")
            return True
            
        user = UserSyncService.import_user_from_keycloak(username)
        if user:
            logger.info(f"Successfully imported user '{username}' from Keycloak")
            return True
        else:
            logger.error(f"Failed to import user '{username}' from Keycloak")
            return False
    else:
        logger.info("Importing all users from Keycloak to database")
        if dry_run:
            logger.info("[DRY RUN] Would import all users from Keycloak")
            return True
            
        total, success, errors = UserSyncService.sync_all_users_from_keycloak()
        logger.info(f"Keycloak sync complete: {success}/{total} users synced successfully, {errors} errors")
        return errors == 0

def export_to_keycloak(app, username=None, dry_run=False):
    """Export users from the database to Keycloak"""
    from infrastructure.auth.user_sync_service import UserSyncService
    from core.models import User
    
    if username:
        logger.info(f"Exporting user '{username}' from database to Keycloak")
        if dry_run:
            logger.info(f"[DRY RUN] Would export user '{username}' to Keycloak")
            return True
            
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User '{username}' not found in database")
            return False
            
        # Since we don't have the user's password, we can't export to Keycloak
        # This function would need to prompt for a password or generate a temporary one
        logger.error("Exporting a specific user to Keycloak requires a password - not supported in this version")
        return False
    else:
        logger.info("Exporting users from database to Keycloak is not fully supported")
        logger.info("This would require setting or resetting passwords for each user")
        return False

def main():
    """Main entry point for the script"""
    parser = setup_parser()
    args = parser.parse_args()
    
    try:
        # Import Flask app and initialize it
        from app_factory import create_app
        app = create_app()
        
        # Put app in application context
        with app.app_context():
            # Run database migration first
            logger.info("Running database migration to ensure schema is up to date")
            try:
                from database.migrations.add_keycloak_id import manual_migration
                from config.settings import SQLALCHEMY_DATABASE_URI
                
                migration_success = manual_migration(SQLALCHEMY_DATABASE_URI)
                if not migration_success:
                    logger.error("Migration failed, cannot continue")
                    return 1
                logger.info("Migration completed successfully")
            except Exception as e:
                logger.error(f"Migration error: {e}")
                logger.error(traceback.format_exc())
                return 1
            
            # Perform synchronization
            if args.direction in ['import', 'both']:
                success = import_from_keycloak(app, args.username, args.dry_run)
                if not success:
                    logger.error("Import from Keycloak failed")
            
            if args.direction in ['export', 'both']:
                success = export_to_keycloak(app, args.username, args.dry_run)
                if not success:
                    logger.error("Export to Keycloak failed or not supported")
                    
        logger.info("Synchronization complete")
        return 0
    
    except Exception as e:
        logger.error(f"Error during synchronization: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())