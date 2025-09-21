namespace DataAnalytics.Core.Models.Analytics;

public class DataProcessingRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public List<string> Operations { get; set; } = new();
    public Dictionary<string, object> Configuration { get; set; } = new();
}

public class DataProcessingResponse
{
    public bool Success { get; set; }
    public string ProcessedDatasetId { get; set; } = string.Empty;
    public Dictionary<string, object> Summary { get; set; } = new();
    public string? ErrorMessage { get; set; }
    public double ProcessingTime { get; set; }
}

public class ModelTrainingRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string Algorithm { get; set; } = string.Empty;
    public string TargetColumn { get; set; } = string.Empty;
    public List<string> Features { get; set; } = new();
    public Dictionary<string, object> Hyperparameters { get; set; } = new();
    public double ValidationSplit { get; set; } = 0.2;
}

public class ModelTrainingResponse
{
    public bool Success { get; set; }
    public string ModelId { get; set; } = string.Empty;
    public Dictionary<string, object> Metrics { get; set; } = new();
    public Dictionary<string, object>? FeatureImportance { get; set; }
    public string? ErrorMessage { get; set; }
    public double TrainingTime { get; set; }
}

public class PredictionRequest
{
    public string ModelId { get; set; } = string.Empty;
    public List<Dictionary<string, object>> Data { get; set; } = new();
}

public class PredictionResponse
{
    public bool Success { get; set; }
    public List<object> Predictions { get; set; } = new();
    public List<Dictionary<string, object>>? Probabilities { get; set; }
    public string? ErrorMessage { get; set; }
}

public class VisualizationRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string ChartType { get; set; } = string.Empty;
    public string XColumn { get; set; } = string.Empty;
    public string? YColumn { get; set; }
    public Dictionary<string, object> Configuration { get; set; } = new();
}

public class VisualizationResponse
{
    public bool Success { get; set; }
    public Dictionary<string, object> ChartData { get; set; } = new();
    public Dictionary<string, object>? Layout { get; set; }
    public string? ErrorMessage { get; set; }
}

public class StatisticalAnalysisRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public string AnalysisType { get; set; } = string.Empty;
    public List<string> Columns { get; set; } = new();
    public Dictionary<string, object> Configuration { get; set; } = new();
}

public class StatisticalAnalysisResponse
{
    public bool Success { get; set; }
    public Dictionary<string, object> Results { get; set; } = new();
    public string? ErrorMessage { get; set; }
}
