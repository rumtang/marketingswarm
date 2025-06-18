"""
Database Configuration Module
Handles environment-based database URL selection for SQLite (dev) and Cloud SQL (production)
"""

import os
from typing import Optional


def get_database_url() -> str:
    """
    Get database URL based on environment
    Returns appropriate connection string for SQLite or Cloud SQL
    """
    # Check if running on Cloud Run
    if os.getenv("K_SERVICE"):  # Cloud Run sets this
        # Use Cloud SQL
        db_user = os.getenv("DB_USER", "app_user")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME", "marketing_swarm")
        instance_connection = os.getenv("INSTANCE_CONNECTION_NAME")
        
        if not db_pass or not instance_connection:
            raise ValueError(
                "Missing required Cloud SQL environment variables: "
                "DB_PASS and INSTANCE_CONNECTION_NAME must be set"
            )
        
        return f"postgresql+asyncpg://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection}"
    else:
        # Use SQLite for local development
        # Check for explicit DATABASE_URL first
        db_url = os.getenv("DATABASE_URL", "sqlite:///./test_marketing_swarm.db")
        # Ensure it has the async driver
        if "sqlite" in db_url and "+aiosqlite" not in db_url:
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        return db_url


def get_sync_database_url() -> str:
    """
    Get synchronous database URL for migrations
    Converts async drivers to sync equivalents
    """
    url = get_database_url()
    # Convert async to sync drivers
    return url.replace("+aiosqlite", "").replace("+asyncpg", "")


def is_cloud_run() -> bool:
    """Check if running on Google Cloud Run"""
    return bool(os.getenv("K_SERVICE"))


def is_postgresql() -> bool:
    """Check if using PostgreSQL database"""
    return "postgresql" in get_database_url()


def get_database_info() -> dict:
    """Get information about current database configuration"""
    url = get_database_url()
    return {
        "type": "PostgreSQL" if "postgresql" in url else "SQLite",
        "is_cloud_run": is_cloud_run(),
        "is_async": "+asyncpg" in url or "+aiosqlite" in url,
        "url_masked": url.split("@")[0] + "@..." if "@" in url else url
    }