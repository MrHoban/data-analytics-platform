using Microsoft.Extensions.Logging;
using Moq;
using StackExchange.Redis;
using Xunit;
using DataAnalytics.Core.Services;
using System.Text.Json;

namespace DataAnalytics.Tests.Services;

public class CacheServiceTests : IDisposable
{
    private readonly Mock<IConnectionMultiplexer> _mockRedis;
    private readonly Mock<IDatabase> _mockDatabase;
    private readonly Mock<ILogger<RedisCacheService>> _mockLogger;
    private readonly RedisCacheService _cacheService;

    public CacheServiceTests()
    {
        _mockRedis = new Mock<IConnectionMultiplexer>();
        _mockDatabase = new Mock<IDatabase>();
        _mockLogger = new Mock<ILogger<RedisCacheService>>();

        _mockRedis.Setup(r => r.GetDatabase(It.IsAny<int>(), It.IsAny<object>()))
                  .Returns(_mockDatabase.Object);

        _cacheService = new RedisCacheService(_mockRedis.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task GetAsync_WhenKeyExists_ReturnsDeserializedObject()
    {
        // Arrange
        var key = "test:key";
        var testObject = new TestObject { Id = 1, Name = "Test" };
        var serializedValue = JsonSerializer.Serialize(testObject, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        _mockDatabase.Setup(db => db.StringGetAsync(key, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(new RedisValue(serializedValue));

        // Act
        var result = await _cacheService.GetAsync<TestObject>(key);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(testObject.Id, result.Id);
        Assert.Equal(testObject.Name, result.Name);
    }

    [Fact]
    public async Task GetAsync_WhenKeyDoesNotExist_ReturnsNull()
    {
        // Arrange
        var key = "nonexistent:key";
        _mockDatabase.Setup(db => db.StringGetAsync(key, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(RedisValue.Null);

        // Act
        var result = await _cacheService.GetAsync<TestObject>(key);

        // Assert
        Assert.Null(result);
    }

    [Fact]
    public async Task SetAsync_WithValidObject_CallsRedisStringSet()
    {
        // Arrange
        var key = "test:key";
        var testObject = new TestObject { Id = 1, Name = "Test" };
        var expiration = TimeSpan.FromMinutes(5);

        // Act
        await _cacheService.SetAsync(key, testObject, expiration);

        // Assert
        _mockDatabase.Verify(
            db => db.StringSetAsync(
                key,
                It.IsAny<RedisValue>(),
                expiration,
                It.IsAny<When>(),
                It.IsAny<CommandFlags>()),
            Times.Once);
    }

    [Fact]
    public async Task RemoveAsync_WithValidKey_CallsRedisKeyDelete()
    {
        // Arrange
        var key = "test:key";

        // Act
        await _cacheService.RemoveAsync(key);

        // Assert
        _mockDatabase.Verify(
            db => db.KeyDeleteAsync(key, It.IsAny<CommandFlags>()),
            Times.Once);
    }

    [Fact]
    public async Task ExistsAsync_WhenKeyExists_ReturnsTrue()
    {
        // Arrange
        var key = "test:key";
        _mockDatabase.Setup(db => db.KeyExistsAsync(key, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(true);

        // Act
        var result = await _cacheService.ExistsAsync(key);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public async Task ExistsAsync_WhenKeyDoesNotExist_ReturnsFalse()
    {
        // Arrange
        var key = "nonexistent:key";
        _mockDatabase.Setup(db => db.KeyExistsAsync(key, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(false);

        // Act
        var result = await _cacheService.ExistsAsync(key);

        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task IncrementAsync_WithValidKey_ReturnsIncrementedValue()
    {
        // Arrange
        var key = "counter:key";
        var incrementValue = 5L;
        var expectedResult = 10L;

        _mockDatabase.Setup(db => db.StringIncrementAsync(key, incrementValue, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(expectedResult);

        // Act
        var result = await _cacheService.IncrementAsync(key, incrementValue);

        // Assert
        Assert.Equal(expectedResult, result);
    }

    [Fact]
    public async Task SetHashAsync_WithValidHash_CallsRedisHashSet()
    {
        // Arrange
        var key = "hash:key";
        var hash = new Dictionary<string, object>
        {
            { "field1", "value1" },
            { "field2", 42 }
        };

        // Act
        await _cacheService.SetHashAsync(key, hash);

        // Assert
        _mockDatabase.Verify(
            db => db.HashSetAsync(
                key,
                It.IsAny<HashEntry[]>(),
                It.IsAny<CommandFlags>()),
            Times.Once);
    }

    [Fact]
    public async Task GetHashFieldAsync_WhenFieldExists_ReturnsDeserializedValue()
    {
        // Arrange
        var key = "hash:key";
        var field = "test:field";
        var testObject = new TestObject { Id = 1, Name = "Test" };
        var serializedValue = JsonSerializer.Serialize(testObject, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        _mockDatabase.Setup(db => db.HashGetAsync(key, field, It.IsAny<CommandFlags>()))
                     .ReturnsAsync(new RedisValue(serializedValue));

        // Act
        var result = await _cacheService.GetHashFieldAsync<TestObject>(key, field);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(testObject.Id, result.Id);
        Assert.Equal(testObject.Name, result.Name);
    }

    [Fact]
    public void CacheKeys_GenerateCorrectKeys()
    {
        // Arrange & Act
        var datasetKey = CacheKeys.Dataset("123");
        var userKey = CacheKeys.User("user456");
        var modelKey = CacheKeys.Model("model789");

        // Assert
        Assert.Equal("dataset:123", datasetKey);
        Assert.Equal("user:user456", userKey);
        Assert.Equal("model:model789", modelKey);
    }

    public void Dispose()
    {
        // Cleanup if needed
    }

    private class TestObject
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
    }
}
