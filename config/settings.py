"""
Configuration settings for Twitter Agent
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    TWITTER_API_KEY: str = Field(..., env="TWITTER_API_KEY")
    TWITTER_API_SECRET: str = Field(..., env="TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: str = Field(..., env="TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: str = Field(..., env="TWITTER_ACCESS_TOKEN_SECRET")
    TWITTER_BEARER_TOKEN: str = Field(..., env="TWITTER_BEARER_TOKEN")
    
    # Fetch.ai Configuration
    FETCH_AI_API_KEY: Optional[str] = Field(None, env="FETCH_AI_API_KEY")
    FETCH_AI_AGENT_ID: Optional[str] = Field(None, env="FETCH_AI_AGENT_ID")
    
    # Composio Configuration
    COMPOSIO_API_KEY: Optional[str] = Field(None, env="COMPOSIO_API_KEY")
    TWITTER_AUTH_CONFIG_ID: Optional[str] = Field(None, env="TWITTER_AUTH_CONFIG_ID")
    
    # Database
    DATABASE_URL: str = Field("sqlite:///./twitter_agent.db", env="DATABASE_URL")
    
    # Redis (for caching and task queue)
    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Application Settings
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    MAX_TWEETS_PER_REQUEST: int = Field(100, env="MAX_TWEETS_PER_REQUEST")
    RATE_LIMIT_DELAY: float = Field(1.0, env="RATE_LIMIT_DELAY")
    
    # Agent Behavior
    DEFAULT_SCHEDULE_INTERVAL: int = Field(3600, env="DEFAULT_SCHEDULE_INTERVAL")  # 1 hour
    MAX_RETRIES: int = Field(3, env="MAX_RETRIES")
    
    # GPT Settings
    GPT_MODEL: str = Field("gpt-4", env="GPT_MODEL")
    GPT_TEMPERATURE: float = Field(0.7, env="GPT_TEMPERATURE")
    MAX_TOKENS: int = Field(2000, env="MAX_TOKENS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
