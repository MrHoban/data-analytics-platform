using System.Text.Json;
using Microsoft.Extensions.Logging;
using StackExchange.Redis;

namespace DataAnalytics.Core.Services;

public interface ICacheService
{
    Task<T?> GetAsync<T>(string key) where T : class;
    Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class;
    Task RemoveAsync(string key);
    Task RemovePatternAsync(string pattern);
    Task<bool> ExistsAsync(string key);
    Task<long> IncrementAsync(string key, long value = 1);
    Task<long> DecrementAsync(string key, long value = 1);
    Task SetHashAsync(string key, Dictionary<string, object> hash);
    Task<Dictionary<string, object>?> GetHashAsync(string key);
    Task SetHashFieldAsync(string key, string field, object value);
    Task<T?> GetHashFieldAsync<T>(string key, string field) where T : class;
}

public class RedisCacheService : ICacheService
{
    private readonly IDatabase _database;
    private readonly ILogger<RedisCacheService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public RedisCacheService(
        IConnectionMultiplexer redis,
        ILogger<RedisCacheService> logger)
    {
        _database = redis.GetDatabase();
        _logger = logger;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false
        };
    }

    public async Task<T?> GetAsync<T>(string key) where T : class
    {
        try
        {
            var value = await _database.StringGetAsync(key);
            
            if (!value.HasValue)
                return null;

            return JsonSerializer.Deserialize<T>(value!, _jsonOptions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting cache value for key {Key}", key);
            return null;
        }
    }

    public async Task SetAsync<T>(string key, T value, TimeSpan? expiration = null) where T : class
    {
        try
        {
            var json = JsonSerializer.Serialize(value, _jsonOptions);
            await _database.StringSetAsync(key, json, expiration);
            
            _logger.LogDebug("Cache value set for key {Key}", key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting cache value for key {Key}", key);
        }
    }

    public async Task RemoveAsync(string key)
    {
        try
        {
            await _database.KeyDeleteAsync(key);
            _logger.LogDebug("Cache value removed for key {Key}", key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error removing cache value for key {Key}", key);
        }
    }

    public async Task RemovePatternAsync(string pattern)
    {
        try
        {
            var server = _database.Multiplexer.GetServer(_database.Multiplexer.GetEndPoints().First());
            var keys = server.Keys(pattern: pattern);
            
            foreach (var key in keys)
            {
                await _database.KeyDeleteAsync(key);
            }
            
            _logger.LogDebug("Cache values removed for pattern {Pattern}", pattern);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error removing cache values for pattern {Pattern}", pattern);
        }
    }

    public async Task<bool> ExistsAsync(string key)
    {
        try
        {
            return await _database.KeyExistsAsync(key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking cache existence for key {Key}", key);
            return false;
        }
    }

    public async Task<long> IncrementAsync(string key, long value = 1)
    {
        try
        {
            return await _database.StringIncrementAsync(key, value);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error incrementing cache value for key {Key}", key);
            return 0;
        }
    }

    public async Task<long> DecrementAsync(string key, long value = 1)
    {
        try
        {
            return await _database.StringDecrementAsync(key, value);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error decrementing cache value for key {Key}", key);
            return 0;
        }
    }

    public async Task SetHashAsync(string key, Dictionary<string, object> hash)
    {
        try
        {
            var hashFields = hash.Select(kvp => new HashEntry(kvp.Key, JsonSerializer.Serialize(kvp.Value, _jsonOptions))).ToArray();
            await _database.HashSetAsync(key, hashFields);
            
            _logger.LogDebug("Hash set for key {Key}", key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting hash for key {Key}", key);
        }
    }

    public async Task<Dictionary<string, object>?> GetHashAsync(string key)
    {
        try
        {
            var hash = await _database.HashGetAllAsync(key);
            
            if (!hash.Any())
                return null;

            var result = new Dictionary<string, object>();
            foreach (var item in hash)
            {
                result[item.Name!] = JsonSerializer.Deserialize<object>(item.Value!, _jsonOptions)!;
            }
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting hash for key {Key}", key);
            return null;
        }
    }

    public async Task SetHashFieldAsync(string key, string field, object value)
    {
        try
        {
            var json = JsonSerializer.Serialize(value, _jsonOptions);
            await _database.HashSetAsync(key, field, json);
            
            _logger.LogDebug("Hash field {Field} set for key {Key}", field, key);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error setting hash field {Field} for key {Key}", field, key);
        }
    }

    public async Task<T?> GetHashFieldAsync<T>(string key, string field) where T : class
    {
        try
        {
            var value = await _database.HashGetAsync(key, field);
            
            if (!value.HasValue)
                return null;

            return JsonSerializer.Deserialize<T>(value!, _jsonOptions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting hash field {Field} for key {Key}", field, key);
            return null;
        }
    }
}

// Cache key helpers
public static class CacheKeys
{
    public const string DatasetPrefix = "dataset:";
    public const string ModelPrefix = "model:";
    public const string UserPrefix = "user:";
    public const string ReportPrefix = "report:";
    public const string StatsPrefix = "stats:";
    
    public static string Dataset(string id) => $"{DatasetPrefix}{id}";
    public static string DatasetList(string userId) => $"{DatasetPrefix}list:{userId}";
    public static string Model(string id) => $"{ModelPrefix}{id}";
    public static string ModelList(string userId) => $"{ModelPrefix}list:{userId}";
    public static string User(string id) => $"{UserPrefix}{id}";
    public static string Report(string id) => $"{ReportPrefix}{id}";
    public static string DashboardStats(string userId) => $"{StatsPrefix}dashboard:{userId}";
}
