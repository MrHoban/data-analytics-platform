"""
Health check endpoints for the Analytics Engine.
"""

from fastapi import APIRouter, Depends
from loguru import logger

from ...database.connection import db_manager

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Data Analytics Engine",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including database connectivity."""
    health_status = {
        "status": "healthy",
        "service": "Data Analytics Engine",
        "version": "1.0.0",
        "components": {}
    }
    
    try:
        # Check database connections
        db_health = await db_manager.health_check()
        health_status["components"]["database"] = {
            "status": "healthy" if db_health["postgresql"] else "unhealthy",
            "postgresql": db_health["postgresql"]
        }
        health_status["components"]["cache"] = {
            "status": "healthy" if db_health["redis"] else "unhealthy",
            "redis": db_health["redis"]
        }
        
        # Overall status
        all_healthy = all([
            db_health["postgresql"],
            db_health["redis"]
        ])
        
        health_status["status"] = "healthy" if all_healthy else "degraded"
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    try:
        # Check if all required services are available
        db_health = await db_manager.health_check()
        
        if db_health["postgresql"] and db_health["redis"]:
            return {"status": "ready"}
        else:
            return {"status": "not ready", "reason": "database connections not available"}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "reason": str(e)}


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}
