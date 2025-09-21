using DataAnalytics.Core.Models;

namespace DataAnalytics.Core.Services;

public interface IPythonAnalyticsService
{
    Task<DataProcessingResult> ProcessDataAsync(string datasetId, DataProcessingOptions options);
    Task<MLTrainingResult> TrainModelAsync(MLTrainingRequest request);
    Task<MLPredictionResult> PredictAsync(string modelId, object[] inputData);
    Task<VisualizationResult> CreateVisualizationAsync(VisualizationRequest request);
    Task<StatisticalAnalysisResult> PerformStatisticalAnalysisAsync(StatisticalAnalysisRequest request);
    Task<bool> HealthCheckAsync();
}

public class DataProcessingOptions
{
    public bool CleanData { get; set; } = true;
    public bool HandleMissingValues { get; set; } = true;
    public bool RemoveOutliers { get; set; } = false;
    public string? EncodingStrategy { get; set; }
    public Dictionary<string, object>? CustomOptions { get; set; }
}

public class DataProcessingResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public int OriginalRows { get; set; }
    public int ProcessedRows { get; set; }
    public int OriginalColumns { get; set; }
    public int ProcessedColumns { get; set; }
    public Dictionary<string, object>? Statistics { get; set; }
    public List<string>? Warnings { get; set; }
}

public class MLTrainingRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string ModelName { get; set; } = string.Empty;
    public string Algorithm { get; set; } = string.Empty;
    public string TargetColumn { get; set; } = string.Empty;
    public List<string> FeatureColumns { get; set; } = new();
    public Dictionary<string, object>? Hyperparameters { get; set; }
    public double TestSize { get; set; } = 0.2;
    public int? RandomState { get; set; }
}

public class MLTrainingResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public string? ModelId { get; set; }
    public double? Accuracy { get; set; }
    public double? Precision { get; set; }
    public double? Recall { get; set; }
    public double? F1Score { get; set; }
    public Dictionary<string, object>? Metrics { get; set; }
    public Dictionary<string, double>? FeatureImportance { get; set; }
}

public class MLPredictionResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public object[]? Predictions { get; set; }
    public double[]? Probabilities { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}

public class VisualizationRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string ChartType { get; set; } = string.Empty;
    public string? XColumn { get; set; }
    public string? YColumn { get; set; }
    public string? ColorColumn { get; set; }
    public string? SizeColumn { get; set; }
    public string? Title { get; set; }
    public int Width { get; set; } = 800;
    public int Height { get; set; } = 600;
    public string Theme { get; set; } = "plotly";
}

public class VisualizationResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public string ChartType { get; set; } = string.Empty;
    public Dictionary<string, object>? ChartData { get; set; }
    public string? ImageBase64 { get; set; }
}

public class StatisticalAnalysisRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string AnalysisType { get; set; } = string.Empty;
    public string? Column1 { get; set; }
    public string? Column2 { get; set; }
    public string? GroupColumn { get; set; }
    public double Alpha { get; set; } = 0.05;
    public Dictionary<string, object>? Parameters { get; set; }
}

public class StatisticalAnalysisResult
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public string TestType { get; set; } = string.Empty;
    public double Statistic { get; set; }
    public double PValue { get; set; }
    public double? CriticalValue { get; set; }
    public List<double>? ConfidenceInterval { get; set; }
    public string Interpretation { get; set; } = string.Empty;
    public bool Significant { get; set; }
    public Dictionary<string, object>? AdditionalResults { get; set; }
}
