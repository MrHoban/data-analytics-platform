"""
Data visualization endpoints for the Analytics Engine.
"""

import base64
import io
from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

# Use non-interactive backend for matplotlib
matplotlib.use('Agg')

router = APIRouter()


class ChartRequest(BaseModel):
    """Request model for creating charts."""
    dataset_id: str
    chart_type: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    title: Optional[str] = None
    width: int = 800
    height: int = 600
    theme: str = "plotly"


class ChartResponse(BaseModel):
    """Response model for chart creation."""
    success: bool
    chart_type: str
    chart_data: Dict
    image_base64: Optional[str] = None


@router.post("/chart")
async def create_chart(request: ChartRequest) -> ChartResponse:
    """
    Create a chart from dataset.
    
    Args:
        request: Chart configuration
        
    Returns:
        Chart data and optional image
    """
    try:
        # TODO: Load dataset from database
        # For now, create mock data
        import numpy as np
        
        np.random.seed(42)
        n_samples = 100
        
        # Create mock dataset based on chart type
        if request.chart_type in ['scatter', 'line']:
            df = pd.DataFrame({
                'x': np.random.normal(0, 1, n_samples),
                'y': np.random.normal(0, 1, n_samples) + np.random.normal(0, 0.1, n_samples),
                'category': np.random.choice(['A', 'B', 'C'], n_samples),
                'size': np.random.uniform(10, 100, n_samples)
            })
        elif request.chart_type == 'bar':
            categories = ['Category A', 'Category B', 'Category C', 'Category D']
            df = pd.DataFrame({
                'category': categories,
                'value': np.random.uniform(10, 100, len(categories))
            })
        elif request.chart_type == 'histogram':
            df = pd.DataFrame({
                'value': np.random.normal(50, 15, n_samples)
            })
        else:
            df = pd.DataFrame({
                'x': np.random.normal(0, 1, n_samples),
                'y': np.random.normal(0, 1, n_samples)
            })
        
        # Create chart based on type
        if request.chart_type == 'scatter':
            fig = create_scatter_plot(df, request)
        elif request.chart_type == 'line':
            fig = create_line_plot(df, request)
        elif request.chart_type == 'bar':
            fig = create_bar_plot(df, request)
        elif request.chart_type == 'histogram':
            fig = create_histogram(df, request)
        elif request.chart_type == 'box':
            fig = create_box_plot(df, request)
        elif request.chart_type == 'heatmap':
            fig = create_heatmap(df, request)
        else:
            raise ValueError(f"Unsupported chart type: {request.chart_type}")
        
        # Convert to JSON
        chart_json = fig.to_json()
        
        # Optionally create static image
        image_base64 = None
        if request.chart_type in ['heatmap']:  # For charts that work better as static images
            img_buffer = io.BytesIO()
            fig.write_image(img_buffer, format='png', width=request.width, height=request.height)
            img_buffer.seek(0)
            image_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        response = ChartResponse(
            success=True,
            chart_type=request.chart_type,
            chart_data={"plotly_json": chart_json},
            image_base64=image_base64
        )
        
        logger.info(f"Chart created successfully: {request.chart_type}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating chart: {str(e)}")


def create_scatter_plot(df: pd.DataFrame, request: ChartRequest):
    """Create a scatter plot."""
    x_col = request.x_column or 'x'
    y_col = request.y_column or 'y'
    color_col = request.color_column
    size_col = request.size_column
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=request.title or f"Scatter Plot: {x_col} vs {y_col}",
        width=request.width,
        height=request.height
    )
    
    return fig


def create_line_plot(df: pd.DataFrame, request: ChartRequest):
    """Create a line plot."""
    x_col = request.x_column or 'x'
    y_col = request.y_column or 'y'
    color_col = request.color_column
    
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=request.title or f"Line Plot: {x_col} vs {y_col}",
        width=request.width,
        height=request.height
    )
    
    return fig


def create_bar_plot(df: pd.DataFrame, request: ChartRequest):
    """Create a bar plot."""
    x_col = request.x_column or 'category'
    y_col = request.y_column or 'value'
    color_col = request.color_column
    
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=request.title or f"Bar Plot: {x_col}",
        width=request.width,
        height=request.height
    )
    
    return fig


def create_histogram(df: pd.DataFrame, request: ChartRequest):
    """Create a histogram."""
    x_col = request.x_column or 'value'
    color_col = request.color_column
    
    fig = px.histogram(
        df,
        x=x_col,
        color=color_col,
        title=request.title or f"Histogram: {x_col}",
        width=request.width,
        height=request.height
    )
    
    return fig


def create_box_plot(df: pd.DataFrame, request: ChartRequest):
    """Create a box plot."""
    x_col = request.x_column
    y_col = request.y_column or 'y'
    color_col = request.color_column
    
    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=request.title or f"Box Plot: {y_col}",
        width=request.width,
        height=request.height
    )
    
    return fig


def create_heatmap(df: pd.DataFrame, request: ChartRequest):
    """Create a heatmap."""
    # For heatmap, use correlation matrix of numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        raise ValueError("No numeric columns found for heatmap")
    
    correlation_matrix = numeric_df.corr()
    
    fig = px.imshow(
        correlation_matrix,
        title=request.title or "Correlation Heatmap",
        width=request.width,
        height=request.height,
        color_continuous_scale='RdBu_r'
    )
    
    return fig


@router.get("/chart-types")
async def get_chart_types():
    """
    Get available chart types.
    
    Returns:
        List of supported chart types
    """
    chart_types = [
        {
            "type": "scatter",
            "name": "Scatter Plot",
            "description": "Shows relationship between two numeric variables",
            "required_columns": ["x", "y"],
            "optional_columns": ["color", "size"]
        },
        {
            "type": "line",
            "name": "Line Plot",
            "description": "Shows trends over time or ordered categories",
            "required_columns": ["x", "y"],
            "optional_columns": ["color"]
        },
        {
            "type": "bar",
            "name": "Bar Chart",
            "description": "Compares values across categories",
            "required_columns": ["x", "y"],
            "optional_columns": ["color"]
        },
        {
            "type": "histogram",
            "name": "Histogram",
            "description": "Shows distribution of a numeric variable",
            "required_columns": ["x"],
            "optional_columns": ["color"]
        },
        {
            "type": "box",
            "name": "Box Plot",
            "description": "Shows distribution and outliers",
            "required_columns": ["y"],
            "optional_columns": ["x", "color"]
        },
        {
            "type": "heatmap",
            "name": "Heatmap",
            "description": "Shows correlation between numeric variables",
            "required_columns": [],
            "optional_columns": []
        }
    ]
    
    return {"chart_types": chart_types}


@router.post("/dashboard")
async def create_dashboard(
    dataset_id: str,
    charts: List[ChartRequest]
):
    """
    Create a dashboard with multiple charts.
    
    Args:
        dataset_id: Dataset identifier
        charts: List of chart configurations
        
    Returns:
        Dashboard with multiple charts
    """
    try:
        dashboard_charts = []
        
        for chart_request in charts:
            chart_request.dataset_id = dataset_id
            chart_response = await create_chart(chart_request)
            dashboard_charts.append(chart_response)
        
        return {
            "success": True,
            "dataset_id": dataset_id,
            "charts": dashboard_charts,
            "chart_count": len(dashboard_charts)
        }
        
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating dashboard: {str(e)}")


@router.get("/datasets/{dataset_id}/columns")
async def get_dataset_columns(dataset_id: str):
    """
    Get column information for a dataset to help with chart creation.
    
    Args:
        dataset_id: Dataset identifier
        
    Returns:
        Column information with data types
    """
    try:
        # TODO: Load actual dataset and analyze columns
        # For now, return mock column information
        
        columns = [
            {"name": "id", "type": "integer", "nullable": False},
            {"name": "name", "type": "string", "nullable": True},
            {"name": "value", "type": "float", "nullable": True},
            {"name": "category", "type": "string", "nullable": True},
            {"name": "date", "type": "datetime", "nullable": True},
            {"name": "count", "type": "integer", "nullable": False}
        ]
        
        # Categorize columns by type for chart recommendations
        numeric_columns = [col["name"] for col in columns if col["type"] in ["integer", "float"]]
        categorical_columns = [col["name"] for col in columns if col["type"] == "string"]
        datetime_columns = [col["name"] for col in columns if col["type"] == "datetime"]
        
        return {
            "dataset_id": dataset_id,
            "columns": columns,
            "column_types": {
                "numeric": numeric_columns,
                "categorical": categorical_columns,
                "datetime": datetime_columns
            },
            "chart_recommendations": {
                "scatter": {"x": numeric_columns, "y": numeric_columns, "color": categorical_columns},
                "line": {"x": datetime_columns + numeric_columns, "y": numeric_columns, "color": categorical_columns},
                "bar": {"x": categorical_columns, "y": numeric_columns, "color": categorical_columns},
                "histogram": {"x": numeric_columns, "color": categorical_columns}
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dataset columns for {dataset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting dataset columns: {str(e)}")
