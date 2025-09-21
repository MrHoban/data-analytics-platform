"""
Error handling middleware for the Analytics Engine.
"""

import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with error handling."""
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Get request ID if available
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            # Log the error
            logger.error(
                f"Unhandled exception in request {request_id}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id,
                    "detail": str(e) if request.app.debug else None
                }
            )
