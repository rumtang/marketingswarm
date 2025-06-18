#!/usr/bin/env python3
"""
Import exported data to Cloud SQL (PostgreSQL)
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from api.conversation_manager import Conversation, Base
from utils.database_config import get_database_url, get_database_info
from loguru import logger


async def import_conversations(json_file: str, target_db_url: str = None):
    """Import conversations from JSON export to database"""
    
    # Check if file exists
    if not Path(json_file).exists():
        logger.error(f"Import file not found: {json_file}")
        return False
    
    # Load data
    logger.info(f"Loading data from {json_file}...")
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    logger.info(f"Found {len(data['conversations'])} conversations to import")
    logger.info(f"Export date: {data.get('export_date', 'Unknown')}")
    
    # Get database URL
    if target_db_url:
        db_url = target_db_url
    else:
        db_url = get_database_url()
    
    db_info = get_database_info()
    logger.info(f"Importing to {db_info['type']} database")
    
    try:
        # Create engine
        engine = create_async_engine(db_url, echo=False)
        
        # Ensure tables exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Import conversations
        imported = 0
        errors = []
        
        async with async_session() as session:
            for i, conv_data in enumerate(data['conversations']):
                try:
                    # Parse datetime fields
                    for field in ['created_at', 'completed_at']:
                        if conv_data.get(field):
                            # Handle various datetime formats
                            if isinstance(conv_data[field], str):
                                try:
                                    # Try ISO format first
                                    conv_data[field] = datetime.fromisoformat(
                                        conv_data[field].replace('Z', '+00:00')
                                    )
                                except:
                                    # Try other formats
                                    conv_data[field] = datetime.strptime(
                                        conv_data[field], "%Y-%m-%d %H:%M:%S"
                                    )
                    
                    # Create conversation object
                    conversation = Conversation(**conv_data)
                    session.add(conversation)
                    
                    # Commit in batches
                    if (i + 1) % 100 == 0:
                        await session.commit()
                        logger.info(f"Imported {i + 1} conversations...")
                    
                    imported += 1
                    
                except Exception as e:
                    error_msg = f"Failed to import conversation {conv_data.get('id', i)}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    # Continue with next conversation
            
            # Final commit
            await session.commit()
        
        # Summary
        logger.success(f"✅ Import completed!")
        logger.info(f"   Imported: {imported}/{len(data['conversations'])} conversations")
        
        if errors:
            logger.warning(f"   Errors: {len(errors)}")
            for error in errors[:5]:
                logger.warning(f"   - {error}")
            if len(errors) > 5:
                logger.warning(f"   ... and {len(errors) - 5} more errors")
        
        # Verify import
        await verify_import(engine, imported)
        
        await engine.dispose()
        return imported > 0
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return False


async def verify_import(engine, expected_count):
    """Verify the import was successful"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM conversations"))
            actual_count = result.scalar()
            
            logger.info(f"\n=== Import Verification ===")
            logger.info(f"Expected conversations: {expected_count}")
            logger.info(f"Actual conversations in database: {actual_count}")
            
            if actual_count >= expected_count:
                logger.success("✓ Import verification passed")
            else:
                logger.warning("⚠️  Fewer conversations in database than expected")
                
    except Exception as e:
        logger.error(f"Verification failed: {e}")


async def clear_existing_data(db_url: str = None):
    """Clear existing conversations before import (optional)"""
    if not db_url:
        db_url = get_database_url()
    
    logger.warning("⚠️  This will DELETE all existing conversations!")
    response = input("Are you sure? (yes/no): ")
    
    if response.lower() != 'yes':
        logger.info("Cancelled")
        return False
    
    try:
        engine = create_async_engine(db_url, echo=False)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("DELETE FROM conversations"))
            await conn.commit()
            
        logger.info("✅ Existing data cleared")
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear data: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description="Import conversation data to Cloud SQL")
    parser.add_argument(
        "json_file",
        help="Path to JSON export file"
    )
    parser.add_argument(
        "--target-db",
        help="Target database URL (default: uses environment config)"
    )
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Clear existing data before import"
    )
    
    args = parser.parse_args()
    
    logger.info("=== Marketing Swarm Data Import ===\n")
    
    # Clear existing data if requested
    if args.clear_existing:
        await clear_existing_data(args.target_db)
    
    # Run import
    success = await import_conversations(args.json_file, args.target_db)
    
    if success:
        logger.success("\n✅ Import completed successfully!")
    else:
        logger.error("\n❌ Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    # Load environment variables if .env exists
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    
    asyncio.run(main())