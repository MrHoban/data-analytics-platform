# Data Analytics Platform API Documentation

## Overview

The Data Analytics Platform provides a comprehensive REST API for data processing, machine learning, visualization, and statistical analysis. The platform consists of two main services:

1. **C# ASP.NET Core API** - Main backend service for user management, data storage, and orchestration
2. **Python FastAPI Analytics Engine** - Specialized service for data processing and machine learning

## Base URLs

- **C# API**: `http://localhost:5000/api`
- **Python Analytics Engine**: `http://localhost:8000`

## Authentication

All API endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
  }
}
```

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe"
}
```

## Dataset Management

### GET /api/datasets
Get user's datasets with pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `pageSize` (optional): Items per page (default: 20)
- `search` (optional): Search query

**Response:**
```json
{
  "datasets": [
    {
      "id": "dataset-id",
      "name": "Sales Data",
      "description": "Monthly sales data",
      "fileName": "sales.csv",
      "fileSize": 2048000,
      "status": "processed",
      "createdAt": "2024-01-16T10:00:00Z"
    }
  ],
  "totalCount": 1,
  "page": 1,
  "pageSize": 20
}
```

### POST /api/datasets/upload
Upload a new dataset.

**Request:** Multipart form data with file

**Response:**
```json
{
  "id": "dataset-id",
  "name": "Uploaded Dataset",
  "status": "processing",
  "message": "Dataset uploaded successfully"
}
```

### GET /api/datasets/{id}
Get dataset details by ID.

**Response:**
```json
{
  "id": "dataset-id",
  "name": "Sales Data",
  "description": "Monthly sales data",
  "fileName": "sales.csv",
  "fileSize": 2048000,
  "status": "processed",
  "metadata": {
    "rows": 1000,
    "columns": 10,
    "columnTypes": {
      "date": "datetime",
      "sales": "numeric",
      "region": "categorical"
    }
  },
  "createdAt": "2024-01-16T10:00:00Z"
}
```

### DELETE /api/datasets/{id}
Delete a dataset.

**Response:**
```json
{
  "success": true,
  "message": "Dataset deleted successfully"
}
```

## Data Processing

### POST /api/analytics/process-data
Process dataset with various operations.

**Request Body:**
```json
{
  "datasetId": "dataset-id",
  "operations": ["clean", "normalize", "encode"],
  "configuration": {
    "remove_duplicates": true,
    "handle_missing": "drop",
    "encoding_strategy": "one_hot"
  }
}
```

**Response:**
```json
{
  "success": true,
  "processedDatasetId": "processed-dataset-id",
  "summary": {
    "rows_processed": 950,
    "columns_processed": 15,
    "duplicates_removed": 50,
    "missing_values_handled": 25
  },
  "processingTime": 2.5
}
```

## Machine Learning

### POST /api/analytics/train-model
Train a machine learning model.

**Request Body:**
```json
{
  "datasetId": "dataset-id",
  "algorithm": "random_forest",
  "targetColumn": "target",
  "features": ["feature1", "feature2", "feature3"],
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  },
  "validationSplit": 0.2
}
```

**Response:**
```json
{
  "success": true,
  "modelId": "model-id",
  "metrics": {
    "accuracy": 0.95,
    "precision": 0.93,
    "recall": 0.92,
    "f1_score": 0.925
  },
  "featureImportance": {
    "feature1": 0.45,
    "feature2": 0.35,
    "feature3": 0.20
  },
  "trainingTime": 15.2
}
```

### POST /api/analytics/predict
Make predictions using a trained model.

**Request Body:**
```json
{
  "modelId": "model-id",
  "data": [
    {
      "feature1": 1.0,
      "feature2": 2.0,
      "feature3": 3.0
    },
    {
      "feature1": 1.5,
      "feature2": 2.5,
      "feature3": 3.5
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "predictions": [0.8, 0.9],
  "probabilities": [
    {
      "class_0": 0.2,
      "class_1": 0.8
    },
    {
      "class_0": 0.1,
      "class_1": 0.9
    }
  ]
}
```

## Data Visualization

### POST /api/analytics/visualize
Generate data visualizations.

**Request Body:**
```json
{
  "datasetId": "dataset-id",
  "chartType": "scatter",
  "xColumn": "feature1",
  "yColumn": "feature2",
  "configuration": {
    "title": "Feature Correlation",
    "colorColumn": "target",
    "size": [800, 600]
  }
}
```

**Response:**
```json
{
  "success": true,
  "chartData": {
    "x": [1.0, 2.0, 3.0],
    "y": [1.5, 2.5, 3.5],
    "type": "scatter",
    "mode": "markers"
  },
  "layout": {
    "title": "Feature Correlation",
    "xaxis": {"title": "feature1"},
    "yaxis": {"title": "feature2"}
  }
}
```

## Statistical Analysis

### POST /api/analytics/statistics
Perform statistical analysis.

**Request Body:**
```json
{
  "datasetId": "dataset-id",
  "analysisType": "correlation",
  "columns": ["feature1", "feature2", "feature3"],
  "configuration": {
    "method": "pearson"
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "correlation_matrix": [
      [1.0, 0.8, 0.6],
      [0.8, 1.0, 0.7],
      [0.6, 0.7, 1.0]
    ],
    "p_values": [
      [0.0, 0.01, 0.05],
      [0.01, 0.0, 0.02],
      [0.05, 0.02, 0.0]
    ]
  }
}
```

## Job Management

### GET /jobs/status/{jobId}
Get the status of an asynchronous job.

**Response:**
```json
{
  "jobId": "job-id",
  "status": "completed",
  "result": {
    "processedRows": 1000,
    "outputDatasetId": "output-dataset-id"
  },
  "completedAt": "2024-01-16T10:05:00Z"
}
```

### GET /jobs/health
Check job processing system health.

**Response:**
```json
{
  "status": "healthy",
  "message": "Job processing system is operational",
  "timestamp": "2024-01-16T10:00:00Z"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "datasetId",
      "issue": "Dataset not found"
    }
  },
  "timestamp": "2024-01-16T10:00:00Z"
}
```

### Common Error Codes

- `VALIDATION_ERROR` - Invalid request data
- `AUTHENTICATION_ERROR` - Invalid or missing authentication
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error
- `RATE_LIMIT_EXCEEDED` - Too many requests

## Rate Limiting

API endpoints are rate limited:
- **Authentication endpoints**: 5 requests per minute
- **Data processing endpoints**: 10 requests per minute
- **Other endpoints**: 100 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642334400
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (1-based)
- `pageSize`: Items per page (max 100)

**Response includes:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalCount": 150,
    "totalPages": 8
  }
}
```

## WebSocket Events

Real-time updates are available via WebSocket connection at `/ws`:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.send(JSON.stringify({
  type: 'authenticate',
  token: 'your-jwt-token'
}));
```

### Event Types
- `job_status_update` - Job processing status changes
- `dataset_processed` - Dataset processing completed
- `model_trained` - Model training completed
