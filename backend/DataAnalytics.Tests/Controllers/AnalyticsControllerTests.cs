using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using DataAnalytics.API.Controllers;
using DataAnalytics.Core.Services;
using DataAnalytics.Core.Models.Analytics;

namespace DataAnalytics.Tests.Controllers;

public class AnalyticsControllerTests
{
    private readonly Mock<IPythonAnalyticsService> _mockAnalyticsService;
    private readonly Mock<ILogger<AnalyticsController>> _mockLogger;
    private readonly AnalyticsController _controller;

    public AnalyticsControllerTests()
    {
        _mockAnalyticsService = new Mock<IPythonAnalyticsService>();
        _mockLogger = new Mock<ILogger<AnalyticsController>>();
        _controller = new AnalyticsController(_mockAnalyticsService.Object, _mockLogger.Object);
    }

    [Fact]
    public async Task ProcessData_WithValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new DataProcessingRequest
        {
            DatasetId = "dataset123",
            Operations = new List<string> { "clean", "normalize" },
            Configuration = new Dictionary<string, object>
            {
                { "remove_duplicates", true },
                { "handle_missing", "drop" }
            }
        };

        var expectedResponse = new DataProcessingResponse
        {
            Success = true,
            ProcessedDatasetId = "processed_dataset123",
            Summary = new Dictionary<string, object>
            {
                { "rows_processed", 1000 },
                { "columns_processed", 10 }
            }
        };

        _mockAnalyticsService.Setup(s => s.ProcessDataAsync(request))
                            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.ProcessData(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<DataProcessingResponse>(okResult.Value);
        Assert.True(response.Success);
        Assert.Equal(expectedResponse.ProcessedDatasetId, response.ProcessedDatasetId);
    }

    [Fact]
    public async Task ProcessData_WithInvalidRequest_ReturnsBadRequest()
    {
        // Arrange
        var request = new DataProcessingRequest
        {
            DatasetId = "", // Invalid empty dataset ID
            Operations = new List<string>()
        };

        // Act
        var result = await _controller.ProcessData(request);

        // Assert
        Assert.IsType<BadRequestObjectResult>(result);
    }

    [Fact]
    public async Task TrainModel_WithValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new ModelTrainingRequest
        {
            DatasetId = "dataset123",
            Algorithm = "random_forest",
            TargetColumn = "target",
            Features = new List<string> { "feature1", "feature2", "feature3" },
            Hyperparameters = new Dictionary<string, object>
            {
                { "n_estimators", 100 },
                { "max_depth", 10 }
            }
        };

        var expectedResponse = new ModelTrainingResponse
        {
            Success = true,
            ModelId = "model123",
            Metrics = new Dictionary<string, object>
            {
                { "accuracy", 0.95 },
                { "precision", 0.93 },
                { "recall", 0.92 }
            }
        };

        _mockAnalyticsService.Setup(s => s.TrainModelAsync(request))
                            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.TrainModel(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<ModelTrainingResponse>(okResult.Value);
        Assert.True(response.Success);
        Assert.Equal(expectedResponse.ModelId, response.ModelId);
    }

    [Fact]
    public async Task MakePredictions_WithValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new PredictionRequest
        {
            ModelId = "model123",
            Data = new List<Dictionary<string, object>>
            {
                new() { { "feature1", 1.0 }, { "feature2", 2.0 } },
                new() { { "feature1", 1.5 }, { "feature2", 2.5 } }
            }
        };

        var expectedResponse = new PredictionResponse
        {
            Success = true,
            Predictions = new List<object> { 0.8, 0.9 },
            Probabilities = new List<Dictionary<string, object>>
            {
                new() { { "class_0", 0.2 }, { "class_1", 0.8 } },
                new() { { "class_0", 0.1 }, { "class_1", 0.9 } }
            }
        };

        _mockAnalyticsService.Setup(s => s.MakePredictionsAsync(request))
                            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.MakePredictions(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<PredictionResponse>(okResult.Value);
        Assert.True(response.Success);
        Assert.Equal(expectedResponse.Predictions.Count, response.Predictions.Count);
    }

    [Fact]
    public async Task GenerateVisualization_WithValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new VisualizationRequest
        {
            DatasetId = "dataset123",
            ChartType = "scatter",
            XColumn = "feature1",
            YColumn = "feature2",
            Configuration = new Dictionary<string, object>
            {
                { "title", "Feature Correlation" },
                { "color_column", "target" }
            }
        };

        var expectedResponse = new VisualizationResponse
        {
            Success = true,
            ChartData = new Dictionary<string, object>
            {
                { "x", new List<double> { 1.0, 2.0, 3.0 } },
                { "y", new List<double> { 1.5, 2.5, 3.5 } },
                { "type", "scatter" }
            },
            Layout = new Dictionary<string, object>
            {
                { "title", "Feature Correlation" },
                { "xaxis", new { title = "feature1" } },
                { "yaxis", new { title = "feature2" } }
            }
        };

        _mockAnalyticsService.Setup(s => s.GenerateVisualizationAsync(request))
                            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.GenerateVisualization(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<VisualizationResponse>(okResult.Value);
        Assert.True(response.Success);
        Assert.NotNull(response.ChartData);
    }

    [Fact]
    public async Task PerformStatisticalAnalysis_WithValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new StatisticalAnalysisRequest
        {
            DatasetId = "dataset123",
            AnalysisType = "correlation",
            Columns = new List<string> { "feature1", "feature2", "feature3" },
            Configuration = new Dictionary<string, object>
            {
                { "method", "pearson" }
            }
        };

        var expectedResponse = new StatisticalAnalysisResponse
        {
            Success = true,
            Results = new Dictionary<string, object>
            {
                { "correlation_matrix", new double[,] { { 1.0, 0.8 }, { 0.8, 1.0 } } },
                { "p_values", new double[,] { { 0.0, 0.01 }, { 0.01, 0.0 } } }
            }
        };

        _mockAnalyticsService.Setup(s => s.PerformStatisticalAnalysisAsync(request))
                            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.PerformStatisticalAnalysis(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<StatisticalAnalysisResponse>(okResult.Value);
        Assert.True(response.Success);
        Assert.NotNull(response.Results);
    }

    [Fact]
    public async Task ProcessData_WhenServiceThrowsException_ReturnsInternalServerError()
    {
        // Arrange
        var request = new DataProcessingRequest
        {
            DatasetId = "dataset123",
            Operations = new List<string> { "clean" }
        };

        _mockAnalyticsService.Setup(s => s.ProcessDataAsync(request))
                            .ThrowsAsync(new Exception("Service error"));

        // Act
        var result = await _controller.ProcessData(request);

        // Assert
        var statusResult = Assert.IsType<ObjectResult>(result);
        Assert.Equal(500, statusResult.StatusCode);
    }
}
