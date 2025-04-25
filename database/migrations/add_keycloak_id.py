"""
Migration script to add keycloak_id field to the user table
"""
import logging
from sqlalchemy import Column, String, create_engine, MetaData, Table
from alembic import op
import sqlalchemy as sa

logger = logging.getLogger(__name__)

def upgrade():
    """
    Add keycloak_id column to the user table
    """
    try:
        # Add keycloak_id column to user table
        op.add_column('user', 
                     sa.Column('keycloak_id', sa.String(36), nullable=True, unique=True))
        
        # Add full_name column if it doesn't exist
        try:
            op.add_column('user', 
                         sa.Column('full_name', sa.String(255), nullable=True))
            logger.info("Added full_name column to user table")
        except Exception as e:
            logger.info(f"full_name column might already exist: {e}")
        
        logger.info("Successfully added keycloak_id column to user table")
    except Exception as e:
        logger.error(f"Error adding columns: {e}")
        raise

def downgrade():
    """
    Remove keycloak_id column from the user table
    """
    try:
        # Remove keycloak_id column
        op.drop_column('user', 'keycloak_id')
        logger.info("Successfully removed keycloak_id column from user table")
    except Exception as e:
        logger.error(f"Error removing keycloak_id column: {e}")
        raise

def manual_migration(db_url):
    """
    Perform manual migration if alembic is not set up
    """
    try:
        engine = create_engine(db_url)
        meta = MetaData()
        meta.reflect(bind=engine)
        
        # Check if user table exists
        if 'user' not in meta.tables:
            logger.error("User table not found in database")
            return False
        
        user_table = meta.tables['user']
        
        # Check if keycloak_id column already exists
        if 'keycloak_id' in user_table.c:
            logger.info("keycloak_id column already exists in user table")
            return True
            
        # Add keycloak_id column
        engine.execute('ALTER TABLE "user" ADD COLUMN keycloak_id VARCHAR(36) UNIQUE')
        
        # Add full_name column if it doesn't exist
        if 'full_name' not in user_table.c:
            engine.execute('ALTER TABLE "user" ADD COLUMN full_name VARCHAR(255)')
            
        logger.info("Successfully performed manual migration for keycloak_id")
        return True
    except Exception as e:
        logger.error(f"Error in manual migration: {e}")
        return False

if __name__ == "__main__":
    # For direct execution of the migration
    import os
    from config.settings import SQLALCHEMY_DATABASE_URI
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Try manual migration since this might be run directly
        success = manual_migration(SQLALCHEMY_DATABASE_URI)
        if success:
            print("Migration completed successfully.")
        else:
            print("Migration failed. Check logs for details.")
    except Exception as e:
        print(f"Migration error: {e}")