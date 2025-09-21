using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using DataAnalytics.Core.Services;
using DataAnalytics.Core.Models;

namespace DataAnalytics.API.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class AnalyticsController : ControllerBase
{
    private readonly IPythonAnalyticsService _pythonAnalyticsService;
    private readonly ILogger<AnalyticsController> _logger;

    public AnalyticsController(
        IPythonAnalyticsService pythonAnalyticsService,
        ILogger<AnalyticsController> logger)
    {
        _pythonAnalyticsService = pythonAnalyticsService;
        _logger = logger;
    }

    [HttpPost("process-data")]
    public async Task<ActionResult<DataProcessingResult>> ProcessData(
        [FromBody] ProcessDataRequest request)
    {
        try
        {
            var options = new DataProcessingOptions
            {
                CleanData = request.CleanData,
                HandleMissingValues = request.HandleMissingValues,
                RemoveOutliers = request.RemoveOutliers,
                EncodingStrategy = request.EncodingStrategy,
                CustomOptions = request.CustomOptions
            };

            var result = await _pythonAnalyticsService.ProcessDataAsync(request.DatasetId, options);
            
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing data for dataset {DatasetId}", request.DatasetId);
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    [HttpPost("train-model")]
    public async Task<ActionResult<MLTrainingResult>> TrainModel(
        [FromBody] TrainModelRequest request)
    {
        try
        {
            var trainingRequest = new MLTrainingRequest
            {
                DatasetId = request.DatasetId,
                ModelName = request.ModelName,
                Algorithm = request.Algorithm,
                TargetColumn = request.TargetColumn,
                FeatureColumns = request.FeatureColumns,
                Hyperparameters = request.Hyperparameters,
                TestSize = request.TestSize,
                RandomState = request.RandomState
            };

            var result = await _pythonAnalyticsService.TrainModelAsync(trainingRequest);
            
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error training model {ModelName}", request.ModelName);
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    [HttpPost("predict")]
    public async Task<ActionResult<MLPredictionResult>> Predict(
        [FromBody] PredictRequest request)
    {
        try
        {
            var result = await _pythonAnalyticsService.PredictAsync(request.ModelId, request.InputData);
            
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error making prediction with model {ModelId}", request.ModelId);
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    [HttpPost("create-visualization")]
    public async Task<ActionResult<VisualizationResult>> CreateVisualization(
        [FromBody] CreateVisualizationRequest request)
    {
        try
        {
            var vizRequest = new VisualizationRequest
            {
                DatasetId = request.DatasetId,
                ChartType = request.ChartType,
                XColumn = request.XColumn,
                YColumn = request.YColumn,
                ColorColumn = request.ColorColumn,
                SizeColumn = request.SizeColumn,
                Title = request.Title,
                Width = request.Width,
                Height = request.Height,
                Theme = request.Theme
            };

            var result = await _pythonAnalyticsService.CreateVisualizationAsync(vizRequest);
            
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating visualization {ChartType}", request.ChartType);
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    [HttpPost("statistical-analysis")]
    public async Task<ActionResult<StatisticalAnalysisResult>> PerformStatisticalAnalysis(
        [FromBody] StatisticalAnalysisRequest request)
    {
        try
        {
            var result = await _pythonAnalyticsService.PerformStatisticalAnalysisAsync(request);
            
            if (!result.Success)
            {
                return BadRequest(result);
            }

            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error performing statistical analysis {AnalysisType}", request.AnalysisType);
            return StatusCode(500, new { message = "Internal server error" });
        }
    }

    [HttpGet("health")]
    [AllowAnonymous]
    public async Task<ActionResult> HealthCheck()
    {
        try
        {
            var isHealthy = await _pythonAnalyticsService.HealthCheckAsync();
            
            if (isHealthy)
            {
                return Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
            }
            else
            {
                return ServiceUnavailable(new { status = "unhealthy", timestamp = DateTime.UtcNow });
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Health check failed");
            return ServiceUnavailable(new { status = "error", message = ex.Message, timestamp = DateTime.UtcNow });
        }
    }

    private ActionResult ServiceUnavailable(object value)
    {
        return StatusCode(503, value);
    }
}

// Request DTOs
public class ProcessDataRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public bool CleanData { get; set; } = true;
    public bool HandleMissingValues { get; set; } = true;
    public bool RemoveOutliers { get; set; } = false;
    public string? EncodingStrategy { get; set; }
    public Dictionary<string, object>? CustomOptions { get; set; }
}

public class TrainModelRequest
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

public class PredictRequest
{
    public string ModelId { get; set; } = string.Empty;
    public object[] InputData { get; set; } = Array.Empty<object>();
}

public class CreateVisualizationRequest
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
