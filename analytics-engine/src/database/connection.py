"""
Database connection management for the Analytics Engine.
"""

import asyncio
from typing import Optional

import asyncpg
import redis.asyncio as redis
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from ..config.settings import get_database_settings, get_redis_settings

# Database instances
async_engine = None
async_session_factory = None
sync_engine = None
sync_session_factory = None
redis_client = None

# SQLAlchemy Base
Base = declarative_base()


async def init_database():
    """Initialize database connections."""
    global async_engine, async_session_factory, sync_engine, sync_session_factory, redis_client
    
    db_settings = get_database_settings()
    redis_settings = get_redis_settings()
    
    try:
        # Initialize PostgreSQL async engine
        async_engine = create_async_engine(
            f"postgresql+asyncpg://{db_settings.username}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.database}",
            pool_size=db_settings.pool_size,
            max_overflow=db_settings.max_overflow,
            pool_timeout=db_settings.pool_timeout,
            pool_recycle=db_settings.pool_recycle,
            echo=False
        )
        
        async_session_factory = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize PostgreSQL sync engine (for pandas operations)
        sync_engine = create_engine(
            db_settings.url,
            pool_size=db_settings.pool_size,
            max_overflow=db_settings.max_overflow,
            pool_timeout=db_settings.pool_timeout,
            pool_recycle=db_settings.pool_recycle,
            echo=False
        )
        
        sync_session_factory = sessionmaker(
            sync_engine,
            expire_on_commit=False
        )
        
        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("PostgreSQL connection established successfully")
        
        # Initialize Redis connection
        redis_client = redis.Redis(
            host=redis_settings.host,
            port=redis_settings.port,
            db=redis_settings.database,
            password=redis_settings.password,
            max_connections=redis_settings.max_connections,
            retry_on_timeout=redis_settings.retry_on_timeout,
            socket_timeout=redis_settings.socket_timeout,
            decode_responses=True
        )
        
        # Test Redis connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        raise


async def close_database():
    """Close database connections."""
    global async_engine, redis_client
    
    try:
        if async_engine:
            await async_engine.dispose()
            logger.info("PostgreSQL async engine disposed")
        
        if sync_engine:
            sync_engine.dispose()
            logger.info("PostgreSQL sync engine disposed")
        
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def get_async_session() -> AsyncSession:
    """Get async database session."""
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session."""
    if not sync_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    with sync_session_factory() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


async def get_redis() -> redis.Redis:
    """Get Redis client."""
    if not redis_client:
        raise RuntimeError("Redis not initialized. Call init_database() first.")
    return redis_client


def get_sync_engine():
    """Get synchronous SQLAlchemy engine for pandas operations."""
    if not sync_engine:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return sync_engine


class DatabaseManager:
    """Database manager for handling connections and operations."""
    
    def __init__(self):
        self.async_engine = None
        self.sync_engine = None
        self.redis_client = None
    
    async def connect(self):
        """Connect to databases."""
        await init_database()
        self.async_engine = async_engine
        self.sync_engine = sync_engine
        self.redis_client = redis_client
    
    async def disconnect(self):
        """Disconnect from databases."""
        await close_database()
    
    async def health_check(self) -> dict:
        """Check database health."""
        health = {
            "postgresql": False,
            "redis": False
        }
        
        try:
            # Check PostgreSQL
            if self.async_engine:
                async with self.async_engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                health["postgresql"] = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
        
        try:
            # Check Redis
            if self.redis_client:
                await self.redis_client.ping()
                health["redis"] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
        
        return health
    
    async def execute_query(self, query: str, params: Optional[dict] = None):
        """Execute a raw SQL query."""
        if not self.async_engine:
            raise RuntimeError("Database not connected")
        
        async with self.async_engine.begin() as conn:
            result = await conn.execute(text(query), params or {})
            return result
    
    async def cache_set(self, key: str, value: str, ttl: int = 3600):
        """Set a value in Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        
        await self.redis_client.setex(key, ttl, value)
    
    async def cache_get(self, key: str) -> Optional[str]:
        """Get a value from Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        
        return await self.redis_client.get(key)
    
    async def cache_delete(self, key: str):
        """Delete a key from Redis cache."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected")
        
        await self.redis_client.delete(key)


# Global database manager instance
db_manager = DatabaseManager()
