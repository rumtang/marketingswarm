"""
Conversation Manager Module
Handles conversation state, persistence, and orchestration
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, text, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from loguru import logger
import json
import os

Base = declarative_base()

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

class ConversationManager:
    """Manages conversation lifecycle and persistence"""
    
    def __init__(self):
        # Import database config
        try:
            from utils.database_config import get_database_url
            self.database_url = get_database_url()
        except ImportError:
            # Fallback if database_config doesn't exist yet
            self.database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test_marketing_swarm.db")
        
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
            
            # Create session factory
            self.async_session = sessionmaker(
                self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            logger.info(f"Database initialized successfully at: {self.database_url}")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    async def create_conversation(
        self, 
        user_query: str, 
        user_id: Optional[str] = None,
        context: Optional[Dict] = None,
        test_mode: bool = False
    ) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        
        try:
            async with self.async_session() as session:
                conversation = Conversation(
                    id=conversation_id,
                    user_id=user_id,
                    user_query=user_query,
                    status="active",
                    created_at=datetime.utcnow(),
                    conversation_metadata=json.dumps({
                        "context": context or {},
                        "test_mode": test_mode
                    })
                )
                
                session.add(conversation)
                await session.commit()
                
                # Track in memory
                self.active_conversations[conversation_id] = {
                    "start_time": datetime.utcnow(),
                    "user_query": user_query,
                    "responses": []
                }
                
                logger.info(f"Created conversation: {conversation_id}")
                return conversation_id
                
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    async def add_agent_response(
        self, 
        conversation_id: str, 
        agent_name: str, 
        response: str
    ):
        """Add an agent response to the conversation"""
        try:
            async with self.async_session() as session:
                # Get conversation - use parameterized query
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if not conversation:
                    logger.error(f"Conversation not found: {conversation_id}")
                    return
                
                # Update agent responses
                agent_responses = json.loads(conversation.agent_responses or "[]")
                agent_responses.append({
                    "agent": agent_name,
                    "response": response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Update in database - use parameterized query
                stmt = text(
                    "UPDATE conversations SET agent_responses = :responses WHERE id = :conv_id"
                )
                await session.execute(
                    stmt, 
                    {"responses": json.dumps(agent_responses), "conv_id": conversation_id}
                )
                await session.commit()
                
                # Update in memory
                if conversation_id in self.active_conversations:
                    self.active_conversations[conversation_id]["responses"].append({
                        "agent": agent_name,
                        "response": response
                    })
                
        except Exception as e:
            logger.error(f"Failed to add agent response: {e}")
    
    async def complete_conversation(self, conversation_id: str):
        """Mark conversation as completed"""
        try:
            async with self.async_session() as session:
                stmt = text(
                    "UPDATE conversations SET status = :status, completed_at = :completed WHERE id = :conv_id"
                )
                await session.execute(
                    stmt,
                    {
                        "status": "completed",
                        "completed": datetime.utcnow(),
                        "conv_id": conversation_id
                    }
                )
                await session.commit()
                
                # Remove from active conversations
                if conversation_id in self.active_conversations:
                    del self.active_conversations[conversation_id]
                
                logger.info(f"Completed conversation: {conversation_id}")
                
        except Exception as e:
            logger.error(f"Failed to complete conversation: {e}")
    
    async def fail_conversation(self, conversation_id: str, error_message: str):
        """Mark conversation as failed"""
        try:
            async with self.async_session() as session:
                stmt = text(
                    """UPDATE conversations 
                    SET status = :status, 
                        completed_at = :completed,
                        error_message = :error
                    WHERE id = :conv_id"""
                )
                await session.execute(
                    stmt,
                    {
                        "status": "failed",
                        "completed": datetime.utcnow(),
                        "error": error_message,
                        "conv_id": conversation_id
                    }
                )
                await session.commit()
                
                # Remove from active conversations
                if conversation_id in self.active_conversations:
                    del self.active_conversations[conversation_id]
                
                logger.warning(f"Failed conversation {conversation_id}: {error_message}")
                
        except Exception as e:
            logger.error(f"Failed to mark conversation as failed: {e}")
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation details"""
        try:
            async with self.async_session() as session:
                stmt = select(Conversation).where(Conversation.id == conversation_id)
                result = await session.execute(stmt)
                conversation = result.scalar_one_or_none()
                
                if conversation:
                    return {
                        "id": conversation.id,
                        "user_query": conversation.user_query,
                        "status": conversation.status,
                        "created_at": conversation.created_at.isoformat(),
                        "agent_responses": json.loads(conversation.agent_responses or "[]"),
                        "metadata": json.loads(conversation.conversation_metadata or "{}")
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None
    
    async def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        try:
            async with self.async_session() as session:
                stmt = select(Conversation).order_by(Conversation.created_at.desc()).limit(limit)
                result = await session.execute(stmt)
                
                conversations = []
                for conversation in result.scalars().all():
                    conversations.append({
                        "id": conversation.id,
                        "user_query": conversation.user_query,
                        "status": conversation.status,
                        "created_at": conversation.created_at.isoformat(),
                        "response_count": len(json.loads(conversation.agent_responses or "[]"))
                    })
                
                return conversations
                
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []
    
    async def clear_all_conversations(self):
        """Clear all conversations (for testing/reset)"""
        try:
            async with self.async_session() as session:
                await session.execute(text("DELETE FROM conversations"))
                await session.commit()
                
                self.active_conversations.clear()
                logger.info("Cleared all conversations")
                
        except Exception as e:
            logger.error(f"Failed to clear conversations: {e}")
    
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
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")