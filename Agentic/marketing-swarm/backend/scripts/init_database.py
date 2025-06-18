#!/usr/bin/env python3
"""
Standalone script to create and initialize the database
Works for both SQLite and PostgreSQL
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from api.conversation_manager import Base
from utils.database_config import get_database_url, get_database_info
from loguru import logger


async def init_database():
    """Initialize the database with all required tables"""
    # Get database info
    db_info = get_database_info()
    db_url = get_database_url()
    
    logger.info(f"Initializing {db_info['type']} database...")
    logger.info(f"Database URL: {db_info['url_masked']}")
    logger.info(f"Running on Cloud Run: {db_info['is_cloud_run']}")
    
    try:
        # Create engine
        engine = create_async_engine(db_url, echo=True)
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.success(f"Database initialized successfully!")
        logger.info(f"Tables created in {db_info['type']} database")
        
        # Dispose of engine
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def verify_database():
    """Verify database is accessible and tables exist"""
    db_url = get_database_url()
    
    try:
        engine = create_async_engine(db_url, echo=False)
        
        async with engine.connect() as conn:
            # Test basic connectivity
            if "postgresql" in db_url:
                result = await conn.execute("SELECT version()")
                version = result.scalar()
                logger.info(f"PostgreSQL version: {version}")
            else:
                result = await conn.execute("SELECT sqlite_version()")
                version = result.scalar()
                logger.info(f"SQLite version: {version}")
            
            # Check if conversations table exists
            if "postgresql" in db_url:
                result = await conn.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'conversations')"
                )
            else:
                result = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'"
                )
            
            table_exists = bool(result.scalar())
            if table_exists:
                logger.success("✓ Conversations table exists")
            else:
                logger.warning("✗ Conversations table does not exist")
        
        await engine.dispose()
        return table_exists
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False


async def main():
    """Main function to initialize and verify database"""
    logger.info("=== Marketing Swarm Database Initialization ===")
    
    # Check for required environment variables if on Cloud Run
    if os.getenv("K_SERVICE"):
        required_vars = ["DB_USER", "DB_PASS", "DB_NAME", "INSTANCE_CONNECTION_NAME"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            logger.error(f"Missing required environment variables for Cloud SQL: {missing}")
            sys.exit(1)
    
    # Initialize database
    await init_database()
    
    # Verify it worked
    logger.info("\nVerifying database setup...")
    if await verify_database():
        logger.success("✓ Database is ready for use!")
    else:
        logger.error("✗ Database verification failed")
        sys.exit(1)


if __name__ == "__main__":
    # Load environment variables if .env exists
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    
    asyncio.run(main())