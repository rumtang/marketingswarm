# Database Migration Plan: SQLite to Cloud SQL for Cloud Run Deployment

## Overview
This plan outlines the complete process for migrating from SQLite (development) to Cloud SQL (production) for Google Cloud Run deployment. The system will use SQLite locally and Cloud SQL when deployed.

## Current State
- **Database**: SQLite (`test_marketing_swarm.db`)
- **ORM**: SQLAlchemy with async support
- **Schema**: Single `conversations` table storing conversation metadata and agent responses
- **Issues**: SQLite doesn't work on Cloud Run due to ephemeral storage

## Target State
- **Local Development**: Continue using SQLite
- **Production (Cloud Run)**: PostgreSQL on Cloud SQL
- **Configuration**: Environment-based database selection
- **Zero Downtime**: Smooth migration path

## Phase 1: Database Initialization & Schema Documentation

### 1.1 Create Database Initialization Script
```python
# scripts/init_database.py
"""
Standalone script to create and initialize the database
Works for both SQLite and PostgreSQL
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from api.conversation_manager import Base

async def init_database():
    # Detect environment
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test_marketing_swarm.db")
    
    # Create engine
    engine = create_async_engine(db_url, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print(f"Database initialized at: {db_url}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
```

### 1.2 Document Current Schema
```sql
-- conversations table schema
CREATE TABLE conversations (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    user_query TEXT NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    agent_responses TEXT DEFAULT '[]',  -- JSON array
    conversation_metadata TEXT DEFAULT '{}',  -- JSON object
    total_cost FLOAT DEFAULT 0.0,
    error_message TEXT
);
```

### 1.3 Create Schema Migration Script
```python
# scripts/migrate_schema.py
"""
Migrate schema between different database types
Handles SQLite -> PostgreSQL differences
"""
```

## Phase 2: Cloud SQL Setup

### 2.1 Create Cloud SQL Instance
```bash
# scripts/setup_cloud_sql.sh
#!/bin/bash

PROJECT_ID="your-project-id"
INSTANCE_NAME="marketing-swarm-db"
REGION="us-central1"
TIER="db-f1-micro"  # Smallest tier for testing

# Create Cloud SQL instance
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=$TIER \
    --region=$REGION \
    --network=default \
    --no-backup \
    --database-flags=max_connections=50

# Create database
gcloud sql databases create marketing_swarm \
    --instance=$INSTANCE_NAME

# Create user
gcloud sql users create app_user \
    --instance=$INSTANCE_NAME \
    --password=secure_password_here

echo "Cloud SQL instance created!"
echo "Connection name: $PROJECT_ID:$REGION:$INSTANCE_NAME"
```

### 2.2 Enable Cloud SQL Auth Proxy
```yaml
# cloudbuild.yaml addition
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['sql', 'instances', 'describe', 'marketing-swarm-db']
    id: 'verify-cloud-sql'
```

## Phase 3: Code Updates

### 3.1 Update Database Configuration
```python
# backend/utils/database_config.py
import os
from typing import Optional

def get_database_url() -> str:
    """
    Get database URL based on environment
    """
    # Check if running on Cloud Run
    if os.getenv("K_SERVICE"):  # Cloud Run sets this
        # Use Cloud SQL
        db_user = os.getenv("DB_USER", "app_user")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME", "marketing_swarm")
        instance_connection = os.getenv("INSTANCE_CONNECTION_NAME")
        
        return f"postgresql+asyncpg://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection}"
    else:
        # Use SQLite for local development
        return "sqlite+aiosqlite:///./test_marketing_swarm.db"

def get_sync_database_url() -> str:
    """Get synchronous database URL for migrations"""
    url = get_database_url()
    # Convert async to sync drivers
    return url.replace("+aiosqlite", "").replace("+asyncpg", "")
```

### 3.2 Update ConversationManager
```python
# backend/api/conversation_manager.py modifications

from utils.database_config import get_database_url

class ConversationManager:
    def __init__(self):
        self.database_url = get_database_url()  # Use new config
        self.engine = None
        self.async_session = None
        self.active_conversations = {}
    
    async def initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # PostgreSQL uses asyncpg, SQLite uses aiosqlite
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,  # Important for Cloud SQL
                pool_size=5,
                max_overflow=10
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
```

### 3.3 Fix SQL Query Compatibility
```python
# backend/api/conversation_manager.py - Fix raw SQL

# OLD - SQL injection vulnerable and not portable:
result = await session.execute(
    f"SELECT * FROM conversations WHERE id = '{conversation_id}'"
)

# NEW - Parameterized and portable:
from sqlalchemy import select
stmt = select(Conversation).where(Conversation.id == conversation_id)
result = await session.execute(stmt)
conversation = result.scalar_one_or_none()
```

### 3.4 Add Database Health Check
```python
# backend/api/conversation_manager.py

async def database_health_check(self) -> bool:
    """Check if database is accessible"""
    try:
        if not self.async_session:
            logger.error("Database session not initialized")
            return False
        
        async with self.async_session() as session:
            # PostgreSQL and SQLite compatible check
            if "postgresql" in self.database_url:
                result = await session.execute(text("SELECT version()"))
            else:
                result = await session.execute(text("SELECT sqlite_version()"))
            
            return result.scalar() is not None
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
```

## Phase 4: Environment Configuration

### 4.1 Local Development (.env)
```bash
# Local development uses SQLite
DATABASE_URL=sqlite:///./test_marketing_swarm.db
ENVIRONMENT=development
```

### 4.2 Cloud Run Environment (.env.production)
```bash
# Cloud Run uses Cloud SQL
DB_USER=app_user
DB_PASS=${SECRET_DB_PASS}
DB_NAME=marketing_swarm
INSTANCE_CONNECTION_NAME=project-id:us-central1:marketing-swarm-db
ENVIRONMENT=production
```

### 4.3 Secret Management
```bash
# Create secret for database password
gcloud secrets create db-pass --data-file=- <<< "your-secure-password"

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding db-pass \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/secretmanager.secretAccessor"
```

## Phase 5: Data Migration

### 5.1 Export SQLite Data
```python
# scripts/export_sqlite_data.py
import sqlite3
import json
from datetime import datetime

def export_conversations():
    conn = sqlite3.connect('test_marketing_swarm.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Export conversations
    cursor.execute("SELECT * FROM conversations")
    conversations = [dict(row) for row in cursor.fetchall()]
    
    # Save to JSON with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversations_export_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            'export_date': datetime.now().isoformat(),
            'conversations': conversations,
            'total_count': len(conversations)
        }, f, indent=2, default=str)
    
    print(f"Exported {len(conversations)} conversations to {filename}")
    conn.close()

if __name__ == "__main__":
    export_conversations()
```

### 5.2 Import to Cloud SQL
```python
# scripts/import_to_cloud_sql.py
import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from api.conversation_manager import Conversation, Base

async def import_conversations(json_file: str):
    # Load data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Connect to Cloud SQL
    engine = create_async_engine(
        os.getenv("CLOUD_SQL_URL"),
        echo=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Import conversations
    async with async_session() as session:
        for conv_data in data['conversations']:
            conversation = Conversation(**conv_data)
            session.add(conversation)
        
        await session.commit()
        print(f"Imported {len(data['conversations'])} conversations")
    
    await engine.dispose()
```

## Phase 6: Deployment Configuration

### 6.1 Update Dockerfile
```dockerfile
# Add Cloud SQL proxy for local connections during build
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy && \
    chmod +x cloud_sql_proxy

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y libpq-dev
```

### 6.2 Update requirements.txt
```python
# Add PostgreSQL support
asyncpg==0.29.0          # Async PostgreSQL driver
psycopg2-binary==2.9.9   # Sync PostgreSQL driver (for migrations)
```

### 6.3 Cloud Run Service Configuration
```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: marketing-swarm-backend
  annotations:
    run.googleapis.com/cloudsql-instances: PROJECT_ID:REGION:marketing-swarm-db
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/marketing-swarm-backend
        env:
        - name: INSTANCE_CONNECTION_NAME
          value: "PROJECT_ID:REGION:marketing-swarm-db"
        - name: DB_USER
          value: "app_user"
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: db-pass
              key: latest
```

## Phase 7: Testing Plan

### 7.1 Local Testing
```bash
# Test SQLite works locally
python scripts/init_database.py
python main.py
# Verify conversations are created and stored

# Test PostgreSQL locally with Docker
docker run -d \
  --name postgres-test \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=marketing_swarm \
  -p 5432:5432 \
  postgres:15

DATABASE_URL=postgresql://postgres:testpass@localhost:5432/marketing_swarm python main.py
```

### 7.2 Cloud SQL Testing
```bash
# Connect to Cloud SQL from local
cloud_sql_proxy -instances=PROJECT_ID:REGION:marketing-swarm-db=tcp:5432 &
DATABASE_URL=postgresql://app_user:password@localhost:5432/marketing_swarm python main.py
```

### 7.3 Migration Testing
```bash
# Test data export/import
python scripts/export_sqlite_data.py
python scripts/import_to_cloud_sql.py conversations_export_*.json
```

## Phase 8: Rollout Plan

### Step 1: Preparation (Day 1)
- [ ] Create Cloud SQL instance
- [ ] Set up secrets in Google Secret Manager
- [ ] Update codebase with database config changes
- [ ] Test locally with both SQLite and PostgreSQL

### Step 2: Staging Deployment (Day 2)
- [ ] Deploy to Cloud Run with Cloud SQL
- [ ] Run integration tests
- [ ] Verify all endpoints work
- [ ] Check performance and connection pooling

### Step 3: Data Migration (Day 3)
- [ ] Export production SQLite data
- [ ] Import to Cloud SQL
- [ ] Verify data integrity
- [ ] Run comparison tests

### Step 4: Production Cutover (Day 4)
- [ ] Deploy new version to Cloud Run
- [ ] Monitor for errors
- [ ] Keep SQLite backup for 30 days
- [ ] Document any issues

## Monitoring & Maintenance

### Cloud SQL Monitoring
```bash
# Set up alerts
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud SQL High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-filter='resource.type="cloudsql_database" AND metric.type="cloudsql.googleapis.com/database/cpu/utilization" AND metric.value > 0.8'
```

### Backup Strategy
```bash
# Automated daily backups
gcloud sql instances patch marketing-swarm-db \
  --backup-start-time=02:00 \
  --enable-point-in-time-recovery \
  --retained-backups-count=7
```

## Cost Estimate

### Development (Current)
- SQLite: $0/month
- Local only, no cloud costs

### Production (Cloud SQL)
- db-f1-micro (shared vCPU, 0.6GB): ~$8/month
- db-g1-small (1 vCPU, 1.7GB): ~$25/month
- Storage: $0.17/GB/month
- Backups: $0.08/GB/month
- **Estimated Total**: $15-35/month for small workload

## Troubleshooting Guide

### Common Issues

1. **Connection Refused**
   - Check Cloud SQL proxy is running
   - Verify instance connection name
   - Check firewall rules

2. **Authentication Failed**
   - Verify secret is accessible
   - Check IAM permissions
   - Ensure password is correct

3. **Slow Queries**
   - Add indexes for conversation_id
   - Use connection pooling
   - Monitor slow query log

4. **Migration Errors**
   - Check data types compatibility
   - Handle NULL values properly
   - Verify JSON fields are valid

## Success Criteria

- [ ] All tests pass with PostgreSQL
- [ ] Zero data loss during migration
- [ ] Response times remain under 500ms
- [ ] No increase in error rates
- [ ] Successful Cloud Run deployment
- [ ] Automated backups working

## Next Steps

1. Review and approve this plan
2. Create Cloud SQL instance
3. Implement code changes
4. Test thoroughly
5. Execute migration
6. Monitor and optimize

This plan ensures a smooth transition from SQLite to Cloud SQL while maintaining data integrity and application functionality.