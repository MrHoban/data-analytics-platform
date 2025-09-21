"""
Message queue service for handling communication with C# API.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import redis.asyncio as redis
from loguru import logger

from ..config.settings import get_settings


class MessageQueueService:
    """Redis-based message queue service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis message queue")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis message queue")
    
    async def publish_message(self, queue_name: str, message: Dict[str, Any]):
        """Publish a message to a queue."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            message_json = json.dumps(message)
            await self.redis_client.lpush(queue_name, message_json)
            
            # Also publish notification
            await self.redis_client.publish(f"{queue_name}:notification", message_json)
            
            logger.info(f"Message published to queue {queue_name}")
        except Exception as e:
            logger.error(f"Error publishing message to queue {queue_name}: {e}")
            raise
    
    async def consume_message(self, queue_name: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Consume a message from a queue."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            result = await self.redis_client.brpop(queue_name, timeout=timeout)
            
            if result:
                _, message_json = result
                message = json.loads(message_json)
                logger.info(f"Message consumed from queue {queue_name}")
                return message
            
            return None
        except Exception as e:
            logger.error(f"Error consuming message from queue {queue_name}: {e}")
            raise
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update job status in Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            result_key = f"job_result:{job_id}"
            
            # Get existing result or create new one
            existing_result = await self.redis_client.get(result_key)
            if existing_result:
                job_result = json.loads(existing_result)
            else:
                job_result = {
                    "jobId": job_id,
                    "status": "pending"
                }
            
            # Update status and result
            job_result["status"] = status
            if result:
                job_result["result"] = result
            if error_message:
                job_result["errorMessage"] = error_message
            
            if status in ["completed", "failed"]:
                job_result["completedAt"] = datetime.utcnow().isoformat()
            
            # Store updated result
            result_json = json.dumps(job_result)
            await self.redis_client.setex(result_key, timedelta(hours=24), result_json)
            
            logger.info(f"Job {job_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error updating job status for {job_id}: {e}")
            raise
    
    async def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job result from Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            result_key = f"job_result:{job_id}"
            result_json = await self.redis_client.get(result_key)
            
            if result_json:
                return json.loads(result_json)
            
            return None
        except Exception as e:
            logger.error(f"Error getting job result for {job_id}: {e}")
            raise


class JobProcessor:
    """Process analytics jobs from the message queue."""
    
    def __init__(self, message_queue: MessageQueueService):
        self.message_queue = message_queue
        self.running = False
        
    async def start(self):
        """Start processing jobs."""
        self.running = True
        logger.info("Job processor started")
        
        # Start consumers for different job types
        tasks = [
            asyncio.create_task(self._consume_queue("analytics:data_processing", self._process_data_job)),
            asyncio.create_task(self._consume_queue("analytics:model_training", self._process_ml_training_job)),
            asyncio.create_task(self._consume_queue("analytics:prediction", self._process_prediction_job)),
            asyncio.create_task(self._consume_queue("analytics:visualization", self._process_visualization_job)),
            asyncio.create_task(self._consume_queue("analytics:statistical_analysis", self._process_statistics_job)),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in job processor: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop processing jobs."""
        self.running = False
        logger.info("Job processor stopped")
    
    async def _consume_queue(self, queue_name: str, processor_func):
        """Consume messages from a specific queue."""
        while self.running:
            try:
                message = await self.message_queue.consume_message(queue_name, timeout=5)
                
                if message:
                    job_id = message.get("id")
                    if job_id:
                        await self.message_queue.update_job_status(job_id, "processing")
                        
                        try:
                            result = await processor_func(message)
                            await self.message_queue.update_job_status(job_id, "completed", result)
                        except Exception as e:
                            logger.error(f"Error processing job {job_id}: {e}")
                            await self.message_queue.update_job_status(
                                job_id, "failed", error_message=str(e)
                            )
                
            except Exception as e:
                logger.error(f"Error consuming from queue {queue_name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_data_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process data processing job."""
        # Import here to avoid circular imports
        from ..core.data_processor import DataProcessor
        
        processor = DataProcessor()
        dataset_id = job.get("datasetId", "")
        parameters = job.get("parameters", {})
        
        # TODO: Load actual dataset and process
        # For now, return mock result
        result = {
            "success": True,
            "originalRows": 1000,
            "processedRows": 950,
            "originalColumns": 10,
            "processedColumns": 12,
            "message": "Data processed successfully"
        }
        
        return result
    
    async def _process_ml_training_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process ML training job."""
        # Import here to avoid circular imports
        from ..core.ml_engine import MLEngine
        
        ml_engine = MLEngine()
        parameters = job.get("parameters", {})
        
        # TODO: Implement actual ML training
        # For now, return mock result
        result = {
            "success": True,
            "modelId": f"model_{int(time.time())}",
            "accuracy": 0.85,
            "message": "Model trained successfully"
        }
        
        return result
    
    async def _process_prediction_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process prediction job."""
        parameters = job.get("parameters", {})
        
        # TODO: Implement actual prediction
        result = {
            "success": True,
            "predictions": [0.8, 0.2, 0.9],
            "message": "Predictions generated successfully"
        }
        
        return result
    
    async def _process_visualization_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process visualization job."""
        parameters = job.get("parameters", {})
        
        # TODO: Implement actual visualization
        result = {
            "success": True,
            "chartType": parameters.get("chartType", "bar"),
            "chartData": {"data": [], "layout": {}},
            "message": "Visualization created successfully"
        }
        
        return result
    
    async def _process_statistics_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process statistical analysis job."""
        parameters = job.get("parameters", {})
        
        # TODO: Implement actual statistical analysis
        result = {
            "success": True,
            "testType": parameters.get("testType", "t_test"),
            "statistic": 2.5,
            "pValue": 0.02,
            "significant": True,
            "message": "Statistical analysis completed successfully"
        }
        
        return result


# Global instances
message_queue_service = MessageQueueService()
job_processor = JobProcessor(message_queue_service)
