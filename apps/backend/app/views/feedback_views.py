"""View schemas for feedback-related API responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FeedbackResponse(BaseModel):
    """Response schema for individual feedback items."""
    id: int = Field(..., description="Unique feedback identifier")
    course_id: str = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Full course title")
    student_email: Optional[str] = Field(None, description="Student email")
    student_name: Optional[str] = Field(None, description="Student name")
    feedback_text: Optional[str] = Field(None, description="Raw feedback content")
    rating: Optional[float] = Field(None, description="1-5 scale rating")
    severity: Optional[str] = Field(None, description="critical|high|medium|low")
    source: str = Field(..., description="canvas|zoho")
    source_id: Optional[str] = Field(None, description="Original platform ID")
    created_at: datetime = Field(..., description="Feedback timestamp")
    last_modified: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Active status")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 123,
                "course_id": "canvas_847",
                "course_name": "IT Leadership Certificate",
                "student_email": "student@example.com",
                "feedback_text": "Video quality is poor in Module 2",
                "rating": 2.5,
                "severity": "high",
                "source": "canvas",
                "source_id": "discussion_post_456",
                "created_at": "2025-09-01T10:30:00Z",
                "last_modified": "2025-09-01T10:30:00Z",
                "is_active": True
            }
        }
    }
    }


class FeedbackCreateRequest(BaseModel):
    """Request schema for creating new feedback."""
    course_id: str = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Course title")
    student_email: Optional[str] = Field(None, description="Student email")
    student_name: Optional[str] = Field(None, description="Student name")
    feedback_text: Optional[str] = Field(None, description="Feedback content")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="1-5 scale rating")
    severity: Optional[str] = Field(None, description="critical|high|medium|low")
    source: str = Field(..., description="canvas|zoho")
    source_id: Optional[str] = Field(None, description="Original platform ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "course_id": "canvas_847",
                "course_name": "IT Leadership Certificate", 
                "student_email": "student@example.com",
                "feedback_text": "The quiz instructions are unclear",
                "rating": 3.0,
                "severity": "medium",
                "source": "canvas",
                "source_id": "quiz_submission_789"
            }
        }
    }


class FeedbackListResponse(BaseModel):
    """Response schema for list of feedback items."""
    feedback: List[FeedbackResponse] = Field(..., description="List of feedback items")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "feedback": [
                    {
                        "id": 123,
                        "course_id": "canvas_847", 
                        "course_name": "IT Leadership Certificate",
                        "student_email": "student@example.com",
                        "feedback_text": "Video quality is poor in Module 2",
                        "rating": 2.5,
                        "severity": "high",
                        "source": "canvas",
                        "source_id": "discussion_post_456",
                        "created_at": "2025-09-01T10:30:00Z",
                        "last_modified": "2025-09-01T10:30:00Z",
                        "is_active": True
                    }
                ],
                "pagination": {
                    "total": 150,
                    "limit": 50,
                    "offset": 0,
                    "has_next": True
                }
            }
        }
    }


class FeedbackStatsResponse(BaseModel):
    """Response schema for feedback statistics."""
    total_feedback: int = Field(..., description="Total feedback count")
    source_distribution: Dict[str, int] = Field(..., description="Feedback by source")
    severity_distribution: Dict[str, int] = Field(..., description="Feedback by severity")
    average_rating: Optional[float] = Field(None, description="Average rating")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_feedback": 245,
                "source_distribution": {
                    "canvas": 180,
                    "zoho": 65
                },
                "severity_distribution": {
                    "critical": 12,
                    "high": 45,
                    "medium": 120,
                    "low": 68
                },
                "average_rating": 3.7
            }
        }
    }