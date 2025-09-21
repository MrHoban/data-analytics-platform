"""
Job management endpoints for the Analytics Engine.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from ...services.message_queue import message_queue_service

router = APIRouter()


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    completed_at: Optional[str] = None


@router.get("/status/{job_id}")
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of a job.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Job status information
    """
    try:
        result = await message_queue_service.get_job_result(job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobStatusResponse(
            job_id=result.get("jobId", job_id),
            status=result.get("status", "unknown"),
            result=result.get("result"),
            error_message=result.get("errorMessage"),
            completed_at=result.get("completedAt")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/update-status/{job_id}")
async def update_job_status(
    job_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
):
    """
    Update the status of a job.
    
    Args:
        job_id: The job identifier
        status: New status
        result: Job result data
        error_message: Error message if failed
        
    Returns:
        Success confirmation
    """
    try:
        await message_queue_service.update_job_status(
            job_id=job_id,
            status=status,
            result=result,
            error_message=error_message
        )
        
        return {"success": True, "message": f"Job {job_id} status updated to {status}"}
        
    except Exception as e:
        logger.error(f"Error updating job status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """
    Health check for job processing system.
    
    Returns:
        Health status
    """
    try:
        # Check if message queue is connected
        if not message_queue_service.redis_client:
            return {"status": "unhealthy", "message": "Message queue not connected"}
        
        # Try to ping Redis
        await message_queue_service.redis_client.ping()
        
        return {
            "status": "healthy",
            "message": "Job processing system is operational",
            "timestamp": "2024-01-16T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Job system health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "timestamp": "2024-01-16T10:00:00Z"
        }
