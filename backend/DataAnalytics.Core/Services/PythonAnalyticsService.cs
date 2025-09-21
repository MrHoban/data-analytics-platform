using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace DataAnalytics.Core.Services;

public class PythonAnalyticsService : IPythonAnalyticsService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonAnalyticsService> _logger;
    private readonly PythonServiceOptions _options;
    private readonly JsonSerializerOptions _jsonOptions;

    public PythonAnalyticsService(
        HttpClient httpClient,
        ILogger<PythonAnalyticsService> logger,
        IOptions<PythonServiceOptions> options)
    {
        _httpClient = httpClient;
        _logger = logger;
        _options = options.Value;
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };

        // Configure HttpClient
        _httpClient.BaseAddress = new Uri(_options.BaseUrl);
        _httpClient.Timeout = TimeSpan.FromMinutes(_options.TimeoutMinutes);
    }

    public async Task<DataProcessingResult> ProcessDataAsync(string datasetId, DataProcessingOptions options)
    {
        try
        {
            _logger.LogInformation("Processing data for dataset {DatasetId}", datasetId);

            var request = new
            {
                dataset_id = datasetId,
                clean_data = options.CleanData,
                handle_missing_values = options.HandleMissingValues,
                remove_outliers = options.RemoveOutliers,
                encoding_strategy = options.EncodingStrategy,
                custom_options = options.CustomOptions
            };

            var response = await PostAsync<DataProcessingResult>("/data/process", request);
            
            _logger.LogInformation("Data processing completed for dataset {DatasetId}. Success: {Success}", 
                datasetId, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing data for dataset {DatasetId}", datasetId);
            return new DataProcessingResult
            {
                Success = false,
                Message = $"Error processing data: {ex.Message}"
            };
        }
    }

    public async Task<MLTrainingResult> TrainModelAsync(MLTrainingRequest request)
    {
        try
        {
            _logger.LogInformation("Training ML model {ModelName} with algorithm {Algorithm}", 
                request.ModelName, request.Algorithm);

            var pythonRequest = new
            {
                dataset_id = request.DatasetId,
                model_name = request.ModelName,
                algorithm = request.Algorithm,
                target_column = request.TargetColumn,
                feature_columns = request.FeatureColumns,
                hyperparameters = request.Hyperparameters,
                test_size = request.TestSize,
                random_state = request.RandomState
            };

            var response = await PostAsync<MLTrainingResult>("/ml/train", pythonRequest);
            
            _logger.LogInformation("ML model training completed. Model: {ModelName}, Success: {Success}", 
                request.ModelName, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error training ML model {ModelName}", request.ModelName);
            return new MLTrainingResult
            {
                Success = false,
                Message = $"Error training model: {ex.Message}"
            };
        }
    }

    public async Task<MLPredictionResult> PredictAsync(string modelId, object[] inputData)
    {
        try
        {
            _logger.LogInformation("Making prediction with model {ModelId}", modelId);

            var request = new
            {
                model_id = modelId,
                input_data = inputData
            };

            var response = await PostAsync<MLPredictionResult>("/ml/predict", request);
            
            _logger.LogInformation("Prediction completed for model {ModelId}. Success: {Success}", 
                modelId, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error making prediction with model {ModelId}", modelId);
            return new MLPredictionResult
            {
                Success = false,
                Message = $"Error making prediction: {ex.Message}"
            };
        }
    }

    public async Task<VisualizationResult> CreateVisualizationAsync(VisualizationRequest request)
    {
        try
        {
            _logger.LogInformation("Creating visualization {ChartType} for dataset {DatasetId}", 
                request.ChartType, request.DatasetId);

            var pythonRequest = new
            {
                dataset_id = request.DatasetId,
                chart_type = request.ChartType,
                x_column = request.XColumn,
                y_column = request.YColumn,
                color_column = request.ColorColumn,
                size_column = request.SizeColumn,
                title = request.Title,
                width = request.Width,
                height = request.Height,
                theme = request.Theme
            };

            var response = await PostAsync<VisualizationResult>("/visualization/chart", pythonRequest);
            
            _logger.LogInformation("Visualization created. Type: {ChartType}, Success: {Success}", 
                request.ChartType, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating visualization {ChartType}", request.ChartType);
            return new VisualizationResult
            {
                Success = false,
                Message = $"Error creating visualization: {ex.Message}"
            };
        }
    }

    public async Task<StatisticalAnalysisResult> PerformStatisticalAnalysisAsync(StatisticalAnalysisRequest request)
    {
        try
        {
            _logger.LogInformation("Performing statistical analysis {AnalysisType} for dataset {DatasetId}", 
                request.AnalysisType, request.DatasetId);

            var pythonRequest = new
            {
                dataset_id = request.DatasetId,
                test_type = request.AnalysisType,
                column1 = request.Column1,
                column2 = request.Column2,
                group_column = request.GroupColumn,
                alpha = request.Alpha,
                parameters = request.Parameters
            };

            var response = await PostAsync<StatisticalAnalysisResult>("/statistics/test", pythonRequest);
            
            _logger.LogInformation("Statistical analysis completed. Type: {AnalysisType}, Success: {Success}", 
                request.AnalysisType, response.Success);

            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing statistical analysis {AnalysisType}", request.AnalysisType);
            return new StatisticalAnalysisResult
            {
                Success = false,
                Message = $"Error performing statistical analysis: {ex.Message}"
            };
        }
    }

    public async Task<bool> HealthCheckAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Python analytics service health check failed");
            return false;
        }
    }

    private async Task<T> PostAsync<T>(string endpoint, object request) where T : new()
    {
        var json = JsonSerializer.Serialize(request, _jsonOptions);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync(endpoint, content);
        
        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync();
            _logger.LogError("Python service request failed. Status: {StatusCode}, Content: {Content}", 
                response.StatusCode, errorContent);
            
            return new T();
        }

        var responseContent = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<T>(responseContent, _jsonOptions);
        
        return result ?? new T();
    }
}

public class PythonServiceOptions
{
    public const string SectionName = "PythonService";
    
    public string BaseUrl { get; set; } = "http://localhost:8000";
    public int TimeoutMinutes { get; set; } = 5;
    public int RetryCount { get; set; } = 3;
    public int RetryDelaySeconds { get; set; } = 2;
}
