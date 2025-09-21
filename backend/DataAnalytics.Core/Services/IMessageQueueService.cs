namespace DataAnalytics.Core.Services;

public interface IMessageQueueService
{
    Task PublishAsync<T>(string queueName, T message) where T : class;
    Task<T?> ConsumeAsync<T>(string queueName, CancellationToken cancellationToken = default) where T : class;
    Task PublishJobAsync(AnalyticsJob job);
    Task<AnalyticsJobResult?> GetJobResultAsync(string jobId, CancellationToken cancellationToken = default);
}

public class AnalyticsJob
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Type { get; set; } = string.Empty;
    public string DatasetId { get; set; } = string.Empty;
    public Dictionary<string, object> Parameters { get; set; } = new();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string UserId { get; set; } = string.Empty;
    public int Priority { get; set; } = 0;
}

public class AnalyticsJobResult
{
    public string JobId { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty; // pending, processing, completed, failed
    public Dictionary<string, object>? Result { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime? CompletedAt { get; set; }
    public TimeSpan? ProcessingTime { get; set; }
}

public static class JobTypes
{
    public const string DataProcessing = "data_processing";
    public const string ModelTraining = "model_training";
    public const string Prediction = "prediction";
    public const string Visualization = "visualization";
    public const string StatisticalAnalysis = "statistical_analysis";
}

public static class JobStatus
{
    public const string Pending = "pending";
    public const string Processing = "processing";
    public const string Completed = "completed";
    public const string Failed = "failed";
    public const string Cancelled = "cancelled";
}
