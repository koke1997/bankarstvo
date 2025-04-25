"""
Migration script to add Keycloak fields to the user table and synchronize users with Keycloak
"""
import os
import sys
import logging
import json
import subprocess
import argparse
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_keycloak_config() -> Dict:
    """
    Load Keycloak configuration from the config file
    
    Returns:
        Dict with Keycloak configuration
    """
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'keycloak.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load Keycloak configuration: {e}")
        return {}

def run_migration(connection_id: Optional[str] = None, connection_name: Optional[str] = None) -> bool:
    """
    Add keycloak_id and full_name columns to the user table if they don't exist
    
    Args:
        connection_id: Optional connection ID override
        connection_name: Optional connection name override
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        # Get connection information
        logger.info("Getting database connection information")
        conn_id = connection_id or "d2sHKRAZndOgOH01CXVgX"  # ID from dbcode-get-connections
        conn_name = connection_name or "Bankarstvo"          # Name from dbcode-get-connections
        
        # First, get databases
        logger.info("Getting database information")
        result = subprocess.run(
            ['code', '--execute-command', 'dbcode.get-databases', '--args', 
             json.dumps({"connectionId": conn_id, "connectionName": conn_name})],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error getting databases: {result.stderr}")
            return False
            
        # Parse the output to get database name (may need to adjust based on actual output)
        # In many cases, the database name will be the same as the connection name
        database_name = "bankarstvo"  # Default database name
        
        # Check if user table exists and its columns
        logger.info(f"Getting table information for database {database_name}")
        
        # Execute query to check if table exists and get columns
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'bankarstvo' 
        AND table_name = 'user';
        """
        
        # Use dbcode to execute the query
        logger.info("Checking existing columns in user table")
        check_result = subprocess.run(
            ['code', '--execute-command', 'dbcode.execute-query', '--args', 
             json.dumps({
                 "connectionId": conn_id, 
                 "connectionName": conn_name,
                 "databaseName": database_name,
                 "query": check_query
             })],
            capture_output=True, text=True
        )
        
        # Parse the result to get column names
        columns = []
        try:
            if check_result.stdout:
                result_data = json.loads(check_result.stdout)
                if 'results' in result_data and len(result_data['results']) > 0:
                    columns = [row[0] for row in result_data['results']]
                    logger.info(f"Found columns: {columns}")
        except Exception as e:
            logger.error(f"Error parsing column results: {e}")
        
        # If user table doesn't exist or we couldn't get columns, report error
        if not columns:
            logger.error("User table not found or couldn't retrieve columns")
            return False
        
        # Add keycloak_id column if it doesn't exist
        if 'keycloak_id' not in columns:
            logger.info("Adding keycloak_id column to user table")
            add_keycloak_query = "ALTER TABLE `user` ADD COLUMN `keycloak_id` VARCHAR(36) UNIQUE;"
            
            keycloak_result = subprocess.run(
                ['code', '--execute-command', 'dbcode.execute-query', '--args', 
                json.dumps({
                    "connectionId": conn_id, 
                    "connectionName": conn_name,
                    "databaseName": database_name,
                    "query": add_keycloak_query
                })],
                capture_output=True, text=True
            )
            
            if keycloak_result.returncode != 0:
                logger.error(f"Error adding keycloak_id column: {keycloak_result.stderr}")
                return False
                
            logger.info("keycloak_id column added successfully")
        else:
            logger.info("keycloak_id column already exists")
            
        # Add full_name column if it doesn't exist
        if 'full_name' not in columns:
            logger.info("Adding full_name column to user table")
            add_fullname_query = "ALTER TABLE `user` ADD COLUMN `full_name` VARCHAR(255);"
            
            fullname_result = subprocess.run(
                ['code', '--execute-command', 'dbcode.execute-query', '--args', 
                json.dumps({
                    "connectionId": conn_id, 
                    "connectionName": conn_name,
                    "databaseName": database_name,
                    "query": add_fullname_query
                })],
                capture_output=True, text=True
            )
            
            if fullname_result.returncode != 0:
                logger.error(f"Error adding full_name column: {fullname_result.stderr}")
                return False
                
            logger.info("full_name column added successfully")
        else:
            logger.info("full_name column already exists")
        
        # Add column to indicate if this user is managed by Keycloak
        if 'keycloak_managed' not in columns:
            logger.info("Adding keycloak_managed column to user table")
            add_managed_query = "ALTER TABLE `user` ADD COLUMN `keycloak_managed` BOOLEAN DEFAULT FALSE;"
            
            managed_result = subprocess.run(
                ['code', '--execute-command', 'dbcode.execute-query', '--args', 
                json.dumps({
                    "connectionId": conn_id, 
                    "connectionName": conn_name,
                    "databaseName": database_name,
                    "query": add_managed_query
                })],
                capture_output=True, text=True
            )
            
            if managed_result.returncode != 0:
                logger.error(f"Error adding keycloak_managed column: {managed_result.stderr}")
                return False
                
            logger.info("keycloak_managed column added successfully")
        else:
            logger.info("keycloak_managed column already exists")
            
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

def run_sync_from_keycloak() -> Tuple[int, int, int]:
    """
    Synchronize users from Keycloak to the local database
    
    Returns:
        Tuple of (total_processed, successful, failed)
    """
    try:
        # Import the required modules - note these imports are local to avoid
        # loading them when only running the migration part
        from infrastructure.auth.keycloak_client import KeycloakClient
        from core.services.user_sync_service import UserSyncService
        
        # Load Keycloak configuration
        keycloak_config = get_keycloak_config()
        if not keycloak_config:
            logger.error("Keycloak configuration not found or invalid")
            return 0, 0, 0
        
        server_url = keycloak_config.get('auth-server-url')
        realm_name = keycloak_config.get('realm')
        client_id = keycloak_config.get('resource')
        client_secret = keycloak_config.get('credentials', {}).get('secret')
        
        if not all([server_url, realm_name, client_id]):
            logger.error("Missing required Keycloak configuration")
            return 0, 0, 0
        
        # Initialize the Keycloak client
        logger.info(f"Initializing Keycloak client for realm {realm_name}")
        keycloak_client = KeycloakClient(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Initialize the sync service
        user_sync_service = UserSyncService(keycloak_client)
        
        # Run a one-time synchronization
        logger.info("Running user synchronization from Keycloak")
        total, success, failed = user_sync_service.sync_all_users(
            two_way=False,  # Only sync from Keycloak to local
            create_missing=True  # Create users that exist in Keycloak but not locally
        )
        
        logger.info(f"Sync completed: {total} processed, {success} successful, {failed} failed")
        return total, success, failed
        
    except ImportError as e:
        logger.error(f"Failed to import required modules for synchronization: {e}")
        logger.error("Make sure that keycloak module is installed (pip install python-keycloak)")
        return 0, 0, 0
    except Exception as e:
        logger.error(f"Error during user synchronization: {e}")
        return 0, 0, 0

def main():
    """
    Main function to parse arguments and run the script
    """
    parser = argparse.ArgumentParser(description='Database migration and Keycloak synchronization')
    parser.add_argument('--skip-migration', action='store_true', help='Skip database migration')
    parser.add_argument('--skip-sync', action='store_true', help='Skip Keycloak synchronization')
    parser.add_argument('--connection-id', help='Override database connection ID')
    parser.add_argument('--connection-name', help='Override database connection name')
    
    args = parser.parse_args()
    
    success = True
    
    # Run migration if not skipped
    if not args.skip_migration:
        logger.info("Running database migration")
        migration_success = run_migration(args.connection_id, args.connection_name)
        if not migration_success:
            logger.error("Database migration failed")
            success = False
        else:
            logger.info("Database migration completed successfully")
    
    # Run synchronization if not skipped and migration was successful (or skipped)
    if not args.skip_sync and success:
        try:
            # Check if python-keycloak is installed
            import keycloak
            logger.info("Running Keycloak user synchronization")
            total, successful, failed = run_sync_from_keycloak()
            if total == 0:
                logger.warning("No users were processed during synchronization")
            elif failed > 0:
                logger.warning(f"Some users failed to sync: {failed} out of {total}")
            else:
                logger.info(f"Keycloak synchronization completed successfully: {successful} users synchronized")
        except ImportError:
            logger.error("Keycloak synchronization requires the python-keycloak package")
            logger.error("Install it with: pip install python-keycloak")
            success = False
    
    return success

if __name__ == "__main__":
    # Run the script
    success = main()
    if success:
        print("Process completed successfully")
        sys.exit(0)
    else:
        print("Process completed with errors")
        sys.exit(1)