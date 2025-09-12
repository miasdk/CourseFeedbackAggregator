"""Common view schemas used across the API."""

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = Field(True, description="Indicates successful operation")
    data: Any = Field(..., description="Response data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": {"id": 1, "message": "Operation completed"},
                "metadata": {
                    "timestamp": "2025-09-10T12:00:00Z",
                    "version": "1.0.0"
                }
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response format."""
    success: bool = Field(False, description="Indicates failed operation")
    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR", 
                    "message": "Invalid course_id format",
                    "details": {
                        "field": "course_id",
                        "expected_format": "source_id (e.g., canvas_847)"
                    }
                },
                "timestamp": "2025-09-10T12:00:00Z"
            }
        }
    }


class HealthResponse(BaseModel):
    """Health check response format."""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp") 
    database: str = Field(..., description="Database connection status")
    version: str = Field(default="1.0.0", description="API version")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-10T12:00:00Z",
                "database": "connected",
                "version": "1.0.0"
            }
        }
    }