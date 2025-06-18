#!/usr/bin/env python3
"""
Simple synchronous database initialization script
Works without greenlet or async complications
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger

# Define the table schema directly here to avoid import issues
Base = declarative_base()

from sqlalchemy import Column, String, DateTime, Text, Float
from datetime import datetime

class Conversation(Base):
    """Conversation database model"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    user_query = Column(Text, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    agent_responses = Column(Text, default="[]")  # JSON array
    conversation_metadata = Column(Text, default="{}")  # JSON object
    total_cost = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)


def init_database():
    """Initialize the database synchronously"""
    # Get database path
    db_path = os.getenv("DATABASE_URL", "sqlite:///./test_marketing_swarm.db")
    # Remove async driver if present
    db_path = db_path.replace("sqlite+aiosqlite:///", "sqlite:///")
    
    logger.info(f"Initializing database at: {db_path}")
    
    try:
        # Create engine
        engine = create_engine(db_path, echo=True)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        logger.success("✅ Database initialized successfully!")
        
        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            logger.info(f"SQLite version: {version}")
            
            # Check if table was created
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            )
            if result.scalar():
                logger.success("✓ Conversations table created successfully")
            else:
                logger.error("✗ Conversations table was not created")
        
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def verify_database():
    """Verify the database structure"""
    db_path = os.getenv("DATABASE_URL", "sqlite:///./test_marketing_swarm.db")
    db_path = db_path.replace("sqlite+aiosqlite:///", "sqlite:///")
    
    try:
        engine = create_engine(db_path, echo=False)
        
        with engine.connect() as conn:
            # Get table schema
            result = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='conversations'")
            )
            schema = result.scalar()
            if schema:
                logger.info("Table schema:")
                logger.info(schema)
                
                # Count rows
                result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
                count = result.scalar()
                logger.info(f"Total conversations: {count}")
            else:
                logger.error("Conversations table not found")
        
        engine.dispose()
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")


if __name__ == "__main__":
    # Load environment variables if .env exists
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    
    logger.info("=== Marketing Swarm Database Initialization (Simple) ===")
    
    if init_database():
        logger.info("\nVerifying database...")
        verify_database()
        
        # Check if the database file was created
        db_file = Path("test_marketing_swarm.db")
        if db_file.exists():
            logger.success(f"✅ Database file created: {db_file.absolute()}")
            logger.info(f"   File size: {db_file.stat().st_size} bytes")
        else:
            logger.warning("⚠️  Database file not found at expected location")
    else:
        logger.error("❌ Database initialization failed")
        sys.exit(1)