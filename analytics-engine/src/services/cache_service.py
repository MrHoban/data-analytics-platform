"""
Caching service for the Analytics Engine.
"""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import redis.asyncio as redis
from loguru import logger

from ..config.settings import get_settings


class CacheService:
    """Redis-based caching service for analytics data."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=False  # We'll handle encoding ourselves
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis cache: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis cache")
    
    async def get(self, key: str, use_pickle: bool = False) -> Optional[Any]:
        """Get a value from cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            value = await self.redis_client.get(key)
            
            if value is None:
                return None
            
            if use_pickle:
                return pickle.loads(value)
            else:
                return json.loads(value.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Error getting cache value for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expiration: Optional[Union[int, timedelta]] = None,
        use_pickle: bool = False
    ):
        """Set a value in cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            if use_pickle:
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = json.dumps(value, default=str).encode('utf-8')
            
            if isinstance(expiration, timedelta):
                expiration = int(expiration.total_seconds())
            
            await self.redis_client.set(key, serialized_value, ex=expiration)
            logger.debug(f"Cache value set for key {key}")
            
        except Exception as e:
            logger.error(f"Error setting cache value for key {key}: {e}")
    
    async def delete(self, key: str):
        """Delete a value from cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            await self.redis_client.delete(key)
            logger.debug(f"Cache value deleted for key {key}")
        except Exception as e:
            logger.error(f"Error deleting cache value for key {key}: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking cache existence for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache value for key {key}: {e}")
            return 0
    
    async def set_hash(self, key: str, mapping: Dict[str, Any]):
        """Set a hash in cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Convert all values to strings
            string_mapping = {k: json.dumps(v, default=str) for k, v in mapping.items()}
            await self.redis_client.hset(key, mapping=string_mapping)
            logger.debug(f"Hash set for key {key}")
        except Exception as e:
            logger.error(f"Error setting hash for key {key}: {e}")
    
    async def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a hash from cache."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            hash_data = await self.redis_client.hgetall(key)
            
            if not hash_data:
                return None
            
            # Convert back from strings
            result = {}
            for k, v in hash_data.items():
                try:
                    result[k.decode('utf-8')] = json.loads(v.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    result[k.decode('utf-8')] = v.decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting hash for key {key}: {e}")
            return None
    
    async def get_hash_field(self, key: str, field: str) -> Optional[Any]:
        """Get a specific field from a hash."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            value = await self.redis_client.hget(key, field)
            
            if value is None:
                return None
            
            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return value.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error getting hash field {field} for key {key}: {e}")
            return None
    
    async def set_hash_field(self, key: str, field: str, value: Any):
        """Set a specific field in a hash."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.hset(key, field, serialized_value)
            logger.debug(f"Hash field {field} set for key {key}")
        except Exception as e:
            logger.error(f"Error setting hash field {field} for key {key}: {e}")


class CacheKeys:
    """Cache key constants and helpers."""
    
    # Prefixes
    DATASET_PREFIX = "dataset:"
    MODEL_PREFIX = "model:"
    STATS_PREFIX = "stats:"
    RESULT_PREFIX = "result:"
    PROFILE_PREFIX = "profile:"
    
    @staticmethod
    def dataset(dataset_id: str) -> str:
        """Cache key for dataset data."""
        return f"{CacheKeys.DATASET_PREFIX}{dataset_id}"
    
    @staticmethod
    def dataset_profile(dataset_id: str) -> str:
        """Cache key for dataset profile/statistics."""
        return f"{CacheKeys.PROFILE_PREFIX}{dataset_id}"
    
    @staticmethod
    def model(model_id: str) -> str:
        """Cache key for ML model."""
        return f"{CacheKeys.MODEL_PREFIX}{model_id}"
    
    @staticmethod
    def model_predictions(model_id: str, input_hash: str) -> str:
        """Cache key for model predictions."""
        return f"{CacheKeys.MODEL_PREFIX}{model_id}:predictions:{input_hash}"
    
    @staticmethod
    def statistics(dataset_id: str, analysis_type: str) -> str:
        """Cache key for statistical analysis results."""
        return f"{CacheKeys.STATS_PREFIX}{dataset_id}:{analysis_type}"
    
    @staticmethod
    def visualization(dataset_id: str, chart_type: str, config_hash: str) -> str:
        """Cache key for visualization results."""
        return f"viz:{dataset_id}:{chart_type}:{config_hash}"
    
    @staticmethod
    def processing_result(dataset_id: str, operation: str) -> str:
        """Cache key for data processing results."""
        return f"{CacheKeys.RESULT_PREFIX}{dataset_id}:{operation}"


class CachedDataProcessor:
    """Data processor with caching capabilities."""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
    
    async def get_or_compute_profile(self, dataset_id: str, compute_func):
        """Get dataset profile from cache or compute it."""
        cache_key = CacheKeys.dataset_profile(dataset_id)
        
        # Try to get from cache first
        cached_profile = await self.cache.get(cache_key)
        if cached_profile:
            logger.info(f"Retrieved dataset profile from cache for {dataset_id}")
            return cached_profile
        
        # Compute profile
        logger.info(f"Computing dataset profile for {dataset_id}")
        profile = await compute_func()
        
        # Cache for 1 hour
        await self.cache.set(cache_key, profile, expiration=timedelta(hours=1))
        
        return profile
    
    async def get_or_compute_statistics(self, dataset_id: str, analysis_type: str, compute_func):
        """Get statistical analysis from cache or compute it."""
        cache_key = CacheKeys.statistics(dataset_id, analysis_type)
        
        # Try to get from cache first
        cached_stats = await self.cache.get(cache_key)
        if cached_stats:
            logger.info(f"Retrieved statistics from cache for {dataset_id}:{analysis_type}")
            return cached_stats
        
        # Compute statistics
        logger.info(f"Computing statistics for {dataset_id}:{analysis_type}")
        stats = await compute_func()
        
        # Cache for 30 minutes
        await self.cache.set(cache_key, stats, expiration=timedelta(minutes=30))
        
        return stats
    
    async def cache_model(self, model_id: str, model_data: Any):
        """Cache a trained model."""
        cache_key = CacheKeys.model(model_id)
        
        # Use pickle for complex model objects
        await self.cache.set(cache_key, model_data, expiration=timedelta(hours=24), use_pickle=True)
        logger.info(f"Cached model {model_id}")
    
    async def get_cached_model(self, model_id: str) -> Optional[Any]:
        """Get a cached model."""
        cache_key = CacheKeys.model(model_id)
        
        model = await self.cache.get(cache_key, use_pickle=True)
        if model:
            logger.info(f"Retrieved model from cache: {model_id}")
        
        return model


# Global cache service instance
cache_service = CacheService()
