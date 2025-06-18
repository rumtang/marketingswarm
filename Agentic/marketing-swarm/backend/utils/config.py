"""
Configuration Module
Centralized configuration management with environment variable validation
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from loguru import logger

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Core Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    FASTAPI_SECRET_KEY: str = Field(..., env="FASTAPI_SECRET_KEY")
    DATABASE_URL: str = Field(default="sqlite:///./marketing_swarm.db", env="DATABASE_URL")
    
    # Safety & Budget Controls
    DAILY_API_BUDGET: float = Field(default=50.00, env="DAILY_API_BUDGET")
    MAX_SEARCHES_PER_SESSION: int = Field(default=25, env="MAX_SEARCHES_PER_SESSION")
    MAX_SEARCHES_PER_AGENT: int = Field(default=5, env="MAX_SEARCHES_PER_AGENT")
    SESSION_TIMEOUT_MINUTES: int = Field(default=10, env="SESSION_TIMEOUT_MINUTES")
    MAX_CONVERSATION_EXCHANGES: int = Field(default=50, env="MAX_CONVERSATION_EXCHANGES")
    
    # Performance Limits
    MAX_CONCURRENT_USERS: int = Field(default=10, env="MAX_CONCURRENT_USERS")
    API_TIMEOUT_SECONDS: int = Field(default=30, env="API_TIMEOUT_SECONDS")
    RESPONSE_TIME_LIMIT: int = Field(default=45, env="RESPONSE_TIME_LIMIT")
    CPU_ALERT_THRESHOLD: float = Field(default=80.0, env="CPU_ALERT_THRESHOLD")
    MEMORY_ALERT_THRESHOLD: float = Field(default=85.0, env="MEMORY_ALERT_THRESHOLD")
    
    # Security Settings
    ENABLE_INPUT_SANITIZATION: bool = Field(default=True, env="ENABLE_INPUT_SANITIZATION")
    LOG_USER_QUERIES: bool = Field(default=False, env="LOG_USER_QUERIES")
    MASK_PII_IN_LOGS: bool = Field(default=True, env="MASK_PII_IN_LOGS")
    REQUIRE_DEMO_MODE_AUTH: bool = Field(default=True, env="REQUIRE_DEMO_MODE_AUTH")
    ADMIN_AUTH_TOKEN: Optional[str] = Field(default=None, env="ADMIN_AUTH_TOKEN")
    
    # Optional Configuration
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SEARCH_CACHE_TTL: int = Field(default=300, env="SEARCH_CACHE_TTL")
    ENABLE_DEMO_FALLBACKS: bool = Field(default=True, env="ENABLE_DEMO_FALLBACKS")
    ENABLE_COMPLIANCE_FILTERS: bool = Field(default=True, env="ENABLE_COMPLIANCE_FILTERS")
    
    # Development Settings
    DEV_MODE: bool = Field(default=False, env="DEV_MODE")
    MOCK_API_RESPONSES: bool = Field(default=False, env="MOCK_API_RESPONSES")
    ENABLE_DEBUG_CONSOLE: bool = Field(default=True, env="ENABLE_DEBUG_CONSOLE")
    
    @validator("OPENAI_API_KEY")
    def validate_api_key(cls, v):
        if not v or v == "your_openai_api_key_here":
            raise ValueError("Valid OpenAI API key required")
        # Allow mock keys for testing
        if v.startswith("sk-mock"):
            logger.warning("Using mock OpenAI API key for testing")
            return v
        if not v.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @validator("DAILY_API_BUDGET")
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError("Daily API budget must be positive")
        if v > 1000:
            logger.warning("Daily API budget exceeds $1000 - are you sure?")
        return v
    
    @validator("CPU_ALERT_THRESHOLD", "MEMORY_ALERT_THRESHOLD")
    def validate_thresholds(cls, v):
        if not 0 < v <= 100:
            raise ValueError("Thresholds must be between 0 and 100")
        return v
    
    @validator("ADMIN_AUTH_TOKEN")
    def generate_admin_token(cls, v):
        if not v and os.getenv("DEV_MODE") != "true":
            # Generate a secure token if not provided
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_safe_dict(self) -> dict:
        """Get settings dict with sensitive values masked"""
        safe_dict = self.dict()
        
        # Mask sensitive values
        if "OPENAI_API_KEY" in safe_dict:
            key = safe_dict["OPENAI_API_KEY"]
            safe_dict["OPENAI_API_KEY"] = f"{key[:7]}...{key[-4:]}" if len(key) > 11 else "***"
        
        if "FASTAPI_SECRET_KEY" in safe_dict:
            safe_dict["FASTAPI_SECRET_KEY"] = "***"
        
        if "ADMIN_AUTH_TOKEN" in safe_dict:
            safe_dict["ADMIN_AUTH_TOKEN"] = "***"
        
        return safe_dict

# Singleton instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            logger.info("Settings loaded successfully")
            logger.debug(f"Configuration: {_settings.get_safe_dict()}")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise
    return _settings

def validate_environment():
    """Validate environment on startup"""
    try:
        settings = get_settings()
        
        # Additional runtime validations
        if settings.DEV_MODE:
            logger.warning("Running in DEVELOPMENT mode - not for production use")
        
        if settings.MOCK_API_RESPONSES:
            logger.warning("Mock API responses enabled - not using real OpenAI API")
        
        if not settings.ENABLE_COMPLIANCE_FILTERS:
            logger.warning("Compliance filters disabled - ensure manual compliance")
        
        if settings.LOG_USER_QUERIES:
            logger.warning("User query logging enabled - ensure privacy compliance")
        
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False