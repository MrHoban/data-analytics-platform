using System.Text.Json;
using Microsoft.Extensions.Logging;
using StackExchange.Redis;

namespace DataAnalytics.Core.Services;

public class RedisMessageQueueService : IMessageQueueService
{
    private readonly IDatabase _database;
    private readonly ISubscriber _subscriber;
    private readonly ILogger<RedisMessageQueueService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public RedisMessageQueueService(
        IConnectionMultiplexer redis,
        ILogger<RedisMessageQueueService> logger)
    {
        _database = redis.GetDatabase();
        _subscriber = redis.GetSubscriber();
        _logger = logger;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false
        };
    }

    public async Task PublishAsync<T>(string queueName, T message) where T : class
    {
        try
        {
            var json = JsonSerializer.Serialize(message, _jsonOptions);
            await _database.ListLeftPushAsync(queueName, json);
            
            // Also publish to subscribers for real-time notifications
            await _subscriber.PublishAsync($"{queueName}:notification", json);
            
            _logger.LogInformation("Message published to queue {QueueName}", queueName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error publishing message to queue {QueueName}", queueName);
            throw;
        }
    }

    public async Task<T?> ConsumeAsync<T>(string queueName, CancellationToken cancellationToken = default) where T : class
    {
        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                var result = await _database.ListRightPopAsync(queueName);
                
                if (result.HasValue)
                {
                    var message = JsonSerializer.Deserialize<T>(result!, _jsonOptions);
                    _logger.LogInformation("Message consumed from queue {QueueName}", queueName);
                    return message;
                }
                
                // Wait a bit before checking again
                await Task.Delay(1000, cancellationToken);
            }
            
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error consuming message from queue {QueueName}", queueName);
            throw;
        }
    }

    public async Task PublishJobAsync(AnalyticsJob job)
    {
        try
        {
            // Store job details
            var jobKey = $"job:{job.Id}";
            var jobJson = JsonSerializer.Serialize(job, _jsonOptions);
            await _database.StringSetAsync(jobKey, jobJson, TimeSpan.FromHours(24));
            
            // Set initial status
            var resultKey = $"job_result:{job.Id}";
            var initialResult = new AnalyticsJobResult
            {
                JobId = job.Id,
                Status = JobStatus.Pending
            };
            var resultJson = JsonSerializer.Serialize(initialResult, _jsonOptions);
            await _database.StringSetAsync(resultKey, resultJson, TimeSpan.FromHours(24));
            
            // Add to appropriate queue based on job type
            var queueName = GetQueueNameForJobType(job.Type);
            await PublishAsync(queueName, job);
            
            _logger.LogInformation("Analytics job {JobId} of type {JobType} published", job.Id, job.Type);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error publishing analytics job {JobId}", job.Id);
            throw;
        }
    }

    public async Task<AnalyticsJobResult?> GetJobResultAsync(string jobId, CancellationToken cancellationToken = default)
    {
        try
        {
            var resultKey = $"job_result:{jobId}";
            var resultJson = await _database.StringGetAsync(resultKey);
            
            if (!resultJson.HasValue)
            {
                return null;
            }
            
            var result = JsonSerializer.Deserialize<AnalyticsJobResult>(resultJson!, _jsonOptions);
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting job result for {JobId}", jobId);
            throw;
        }
    }

    private static string GetQueueNameForJobType(string jobType)
    {
        return jobType switch
        {
            JobTypes.DataProcessing => "analytics:data_processing",
            JobTypes.ModelTraining => "analytics:model_training",
            JobTypes.Prediction => "analytics:prediction",
            JobTypes.Visualization => "analytics:visualization",
            JobTypes.StatisticalAnalysis => "analytics:statistical_analysis",
            _ => "analytics:general"
        };
    }
}

// Extension methods for easier job management
public static class MessageQueueExtensions
{
    public static async Task UpdateJobStatusAsync(
        this IMessageQueueService messageQueue,
        string jobId,
        string status,
        Dictionary<string, object>? result = null,
        string? errorMessage = null)
    {
        if (messageQueue is RedisMessageQueueService redisService)
        {
            await redisService.UpdateJobStatusInternalAsync(jobId, status, result, errorMessage);
        }
    }
}

// Internal extension for Redis implementation
internal static class RedisMessageQueueExtensions
{
    internal static async Task UpdateJobStatusInternalAsync(
        this RedisMessageQueueService service,
        string jobId,
        string status,
        Dictionary<string, object>? result = null,
        string? errorMessage = null)
    {
        // This would need access to the Redis connection
        // For now, we'll implement this as a separate method in the service
    }
}
