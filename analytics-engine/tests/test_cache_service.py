"""
Tests for the cache service.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta

from src.services.cache_service import CacheService, CacheKeys, CachedDataProcessor


@pytest.fixture
def cache_service():
    """Create a cache service instance for testing."""
    return CacheService()


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock()
    mock_redis.get = AsyncMock()
    mock_redis.set = AsyncMock()
    mock_redis.delete = AsyncMock()
    mock_redis.exists = AsyncMock()
    mock_redis.incrby = AsyncMock()
    mock_redis.hset = AsyncMock()
    mock_redis.hgetall = AsyncMock()
    mock_redis.hget = AsyncMock()
    mock_redis.close = AsyncMock()
    return mock_redis


class TestCacheService:
    """Test cases for CacheService."""

    @pytest.mark.asyncio
    async def test_connect_success(self, cache_service, mock_redis):
        """Test successful Redis connection."""
        with patch('redis.asyncio.from_url', return_value=mock_redis):
            await cache_service.connect()
            
            assert cache_service.redis_client is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, cache_service):
        """Test Redis connection failure."""
        with patch('redis.asyncio.from_url', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception, match="Connection failed"):
                await cache_service.connect()

    @pytest.mark.asyncio
    async def test_get_existing_key(self, cache_service, mock_redis):
        """Test getting an existing key from cache."""
        cache_service.redis_client = mock_redis
        test_data = {"key": "value", "number": 42}
        mock_redis.get.return_value = json.dumps(test_data).encode('utf-8')
        
        result = await cache_service.get("test:key")
        
        assert result == test_data
        mock_redis.get.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache_service, mock_redis):
        """Test getting a non-existent key from cache."""
        cache_service.redis_client = mock_redis
        mock_redis.get.return_value = None
        
        result = await cache_service.get("nonexistent:key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("nonexistent:key")

    @pytest.mark.asyncio
    async def test_set_with_expiration(self, cache_service, mock_redis):
        """Test setting a value with expiration."""
        cache_service.redis_client = mock_redis
        test_data = {"key": "value"}
        expiration = timedelta(minutes=5)
        
        await cache_service.set("test:key", test_data, expiration)
        
        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        assert args[0] == "test:key"
        assert kwargs.get('ex') == 300  # 5 minutes in seconds

    @pytest.mark.asyncio
    async def test_set_without_expiration(self, cache_service, mock_redis):
        """Test setting a value without expiration."""
        cache_service.redis_client = mock_redis
        test_data = {"key": "value"}
        
        await cache_service.set("test:key", test_data)
        
        mock_redis.set.assert_called_once()
        args, kwargs = mock_redis.set.call_args
        assert args[0] == "test:key"
        assert kwargs.get('ex') is None

    @pytest.mark.asyncio
    async def test_delete_key(self, cache_service, mock_redis):
        """Test deleting a key from cache."""
        cache_service.redis_client = mock_redis
        
        await cache_service.delete("test:key")
        
        mock_redis.delete.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_exists_true(self, cache_service, mock_redis):
        """Test checking if a key exists (returns True)."""
        cache_service.redis_client = mock_redis
        mock_redis.exists.return_value = 1
        
        result = await cache_service.exists("test:key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_exists_false(self, cache_service, mock_redis):
        """Test checking if a key exists (returns False)."""
        cache_service.redis_client = mock_redis
        mock_redis.exists.return_value = 0
        
        result = await cache_service.exists("test:key")
        
        assert result is False
        mock_redis.exists.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_increment(self, cache_service, mock_redis):
        """Test incrementing a value."""
        cache_service.redis_client = mock_redis
        mock_redis.incrby.return_value = 5
        
        result = await cache_service.increment("counter:key", 3)
        
        assert result == 5
        mock_redis.incrby.assert_called_once_with("counter:key", 3)

    @pytest.mark.asyncio
    async def test_set_hash(self, cache_service, mock_redis):
        """Test setting a hash."""
        cache_service.redis_client = mock_redis
        test_hash = {"field1": "value1", "field2": 42}
        
        await cache_service.set_hash("hash:key", test_hash)
        
        mock_redis.hset.assert_called_once()
        args, kwargs = mock_redis.hset.call_args
        assert args[0] == "hash:key"
        assert "mapping" in kwargs

    @pytest.mark.asyncio
    async def test_get_hash_existing(self, cache_service, mock_redis):
        """Test getting an existing hash."""
        cache_service.redis_client = mock_redis
        mock_hash_data = {
            b"field1": b'"value1"',
            b"field2": b"42"
        }
        mock_redis.hgetall.return_value = mock_hash_data
        
        result = await cache_service.get_hash("hash:key")
        
        assert result is not None
        assert result["field1"] == "value1"
        assert result["field2"] == 42

    @pytest.mark.asyncio
    async def test_get_hash_nonexistent(self, cache_service, mock_redis):
        """Test getting a non-existent hash."""
        cache_service.redis_client = mock_redis
        mock_redis.hgetall.return_value = {}
        
        result = await cache_service.get_hash("nonexistent:hash")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_hash_field(self, cache_service, mock_redis):
        """Test getting a specific hash field."""
        cache_service.redis_client = mock_redis
        mock_redis.hget.return_value = b'"test_value"'
        
        result = await cache_service.get_hash_field("hash:key", "field1")
        
        assert result == "test_value"
        mock_redis.hget.assert_called_once_with("hash:key", "field1")

    @pytest.mark.asyncio
    async def test_set_hash_field(self, cache_service, mock_redis):
        """Test setting a specific hash field."""
        cache_service.redis_client = mock_redis
        
        await cache_service.set_hash_field("hash:key", "field1", "test_value")
        
        mock_redis.hset.assert_called_once_with("hash:key", "field1", '"test_value"')


class TestCacheKeys:
    """Test cases for CacheKeys helper class."""

    def test_dataset_key(self):
        """Test dataset cache key generation."""
        key = CacheKeys.dataset("dataset123")
        assert key == "dataset:dataset123"

    def test_dataset_profile_key(self):
        """Test dataset profile cache key generation."""
        key = CacheKeys.dataset_profile("dataset123")
        assert key == "profile:dataset123"

    def test_model_key(self):
        """Test model cache key generation."""
        key = CacheKeys.model("model456")
        assert key == "model:model456"

    def test_model_predictions_key(self):
        """Test model predictions cache key generation."""
        key = CacheKeys.model_predictions("model456", "hash123")
        assert key == "model:model456:predictions:hash123"

    def test_statistics_key(self):
        """Test statistics cache key generation."""
        key = CacheKeys.statistics("dataset123", "correlation")
        assert key == "stats:dataset123:correlation"

    def test_visualization_key(self):
        """Test visualization cache key generation."""
        key = CacheKeys.visualization("dataset123", "scatter", "config456")
        assert key == "viz:dataset123:scatter:config456"

    def test_processing_result_key(self):
        """Test processing result cache key generation."""
        key = CacheKeys.processing_result("dataset123", "clean")
        assert key == "result:dataset123:clean"


class TestCachedDataProcessor:
    """Test cases for CachedDataProcessor."""

    @pytest.fixture
    def cached_processor(self, cache_service):
        """Create a cached data processor for testing."""
        return CachedDataProcessor(cache_service)

    @pytest.mark.asyncio
    async def test_get_or_compute_profile_cached(self, cached_processor, mock_redis):
        """Test getting profile from cache."""
        cached_processor.cache.redis_client = mock_redis
        cached_profile = {"rows": 1000, "columns": 10}
        mock_redis.get.return_value = json.dumps(cached_profile).encode('utf-8')
        
        compute_func = AsyncMock()
        
        result = await cached_processor.get_or_compute_profile("dataset123", compute_func)
        
        assert result == cached_profile
        compute_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_compute_profile_not_cached(self, cached_processor, mock_redis):
        """Test computing profile when not cached."""
        cached_processor.cache.redis_client = mock_redis
        mock_redis.get.return_value = None
        
        computed_profile = {"rows": 1000, "columns": 10}
        compute_func = AsyncMock(return_value=computed_profile)
        
        result = await cached_processor.get_or_compute_profile("dataset123", compute_func)
        
        assert result == computed_profile
        compute_func.assert_called_once()
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_model(self, cached_processor, mock_redis):
        """Test caching a model."""
        cached_processor.cache.redis_client = mock_redis
        model_data = {"type": "random_forest", "params": {"n_estimators": 100}}
        
        await cached_processor.cache_model("model123", model_data)
        
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cached_model_exists(self, cached_processor, mock_redis):
        """Test getting a cached model that exists."""
        cached_processor.cache.redis_client = mock_redis
        import pickle
        model_data = {"type": "random_forest"}
        mock_redis.get.return_value = pickle.dumps(model_data)
        
        result = await cached_processor.get_cached_model("model123")
        
        assert result == model_data

    @pytest.mark.asyncio
    async def test_get_cached_model_not_exists(self, cached_processor, mock_redis):
        """Test getting a cached model that doesn't exist."""
        cached_processor.cache.redis_client = mock_redis
        mock_redis.get.return_value = None
        
        result = await cached_processor.get_cached_model("model123")
        
        assert result is None
