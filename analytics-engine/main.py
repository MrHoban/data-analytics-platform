"""
Data Analytics Platform - Python Analytics Engine
Main FastAPI application for data processing, machine learning, and analytics.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_client import make_asgi_app

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import get_settings
from src.database.connection import init_database, close_database
from src.api.routes import (
    data_processing,
    machine_learning,
    visualization,
    statistics,
    health,
    jobs
)
from src.middleware.logging import LoggingMiddleware
from src.middleware.error_handling import ErrorHandlingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Data Analytics Engine...")
    
    # Initialize database connection
    await init_database()

    # Initialize message queue
    from src.services.message_queue import message_queue_service, job_processor
    await message_queue_service.connect()

    # Initialize cache service
    from src.services.cache_service import cache_service
    await cache_service.connect()

    # Start job processor in background
    import asyncio
    job_processor_task = asyncio.create_task(job_processor.start())

    # Initialize ML models cache
    # TODO: Load pre-trained models

    logger.info("Data Analytics Engine started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Data Analytics Engine...")

    # Stop job processor
    job_processor.stop()
    if 'job_processor_task' in locals():
        job_processor_task.cancel()
        try:
            await job_processor_task
        except asyncio.CancelledError:
            pass

    # Disconnect services
    await message_queue_service.disconnect()
    await cache_service.disconnect()

    await close_database()
    logger.info("Data Analytics Engine shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Data Analytics Engine",
        description="Python-based analytics engine for data processing, machine learning, and visualization",
        version="1.0.0",
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
    
    # Add custom middleware
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Include API routes
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(data_processing.router, prefix="/api/v1/data", tags=["Data Processing"])
    app.include_router(machine_learning.router, prefix="/api/v1/ml", tags=["Machine Learning"])
    app.include_router(visualization.router, prefix="/api/v1/viz", tags=["Visualization"])
    app.include_router(statistics.router, prefix="/api/v1/stats", tags=["Statistics"])
    app.include_router(jobs.router, prefix="/jobs", tags=["Job Management"])
    
    # Add Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception handler caught: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "detail": str(exc) if settings.environment == "development" else None
            }
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return {
            "service": "Data Analytics Engine",
            "version": "1.0.0",
            "status": "running",
            "environment": settings.environment,
            "docs_url": "/docs" if settings.environment == "development" else None
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if settings.environment == "development" else "INFO"
    )
    
    # Add file logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "analytics_engine_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info",
        access_log=True
    )
