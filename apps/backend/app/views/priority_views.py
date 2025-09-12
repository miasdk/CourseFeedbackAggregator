"""View schemas for priority-related API responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ScoringBreakdown(BaseModel):
    """Schema for priority scoring breakdown."""
    impact_score: float = Field(..., description="Student impact factor (1-5)")
    urgency_score: float = Field(..., description="Time sensitivity factor (1-5)")
    effort_score: float = Field(..., description="Implementation effort (1-5)")
    strategic_score: float = Field(..., description="Strategic alignment (1-5)")
    trend_score: float = Field(..., description="Issue trajectory (1-5)")
    weights_used: Dict[str, float] = Field(..., description="Weights used in calculation")


class EvidenceData(BaseModel):
    """Schema for evidence supporting priority recommendations."""
    student_quotes: List[Dict[str, Any]] = Field(..., description="Student feedback quotes")
    source_links: List[Dict[str, Any]] = Field(..., description="Links to original sources")
    affected_students: int = Field(..., description="Number of affected students")
    confidence_score: float = Field(..., description="Confidence in recommendation")


class ReviewResponse(BaseModel):
    """Response schema for priority reviews."""
    id: int = Field(..., description="Review ID")
    priority_id: int = Field(..., description="Associated priority ID")
    reviewer_name: str = Field(..., description="Reviewer name")
    validated: bool = Field(..., description="Validation status")
    action_taken: Optional[str] = Field(None, description="Action taken")
    notes: Optional[str] = Field(None, description="Reviewer notes")
    created_at: datetime = Field(..., description="Review timestamp")

    model_config = {
        "from_attributes": True
    }


class PriorityResponse(BaseModel):
    """Response schema for individual priority recommendations."""
    id: int = Field(..., description="Priority ID")
    course_id: str = Field(..., description="Course identifier")
    issue_summary: str = Field(..., description="Generated issue description")
    priority_score: int = Field(..., description="1-5 final priority score")
    scoring_breakdown: ScoringBreakdown = Field(..., description="Factor breakdown")
    students_affected: int = Field(..., description="Count of affected students")
    evidence: EvidenceData = Field(..., description="Supporting evidence")
    feedback_ids: List[int] = Field(..., description="Source feedback IDs")
    reviews: Optional[List[ReviewResponse]] = Field(None, description="Review history")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 456,
                "course_id": "canvas_847",
                "issue_summary": "Video quality issues affecting student comprehension",
                "priority_score": 8,
                "scoring_breakdown": {
                    "impact_score": 9.2,
                    "urgency_score": 8.5,
                    "effort_score": 6.0,
                    "strategic_score": 7.0,
                    "trend_score": 8.0,
                    "weights_used": {
                        "impact_weight": 0.40,
                        "urgency_weight": 0.35,
                        "effort_weight": 0.25,
                        "strategic_weight": 0.15,
                        "trend_weight": 0.10
                    }
                },
                "students_affected": 23,
                "evidence": {
                    "student_quotes": [
                        {
                            "feedback_id": 123,
                            "quote": "Video quality is poor and hard to follow",
                            "source": "canvas",
                            "source_id": "discussion_post_456"
                        }
                    ],
                    "source_links": [
                        {
                            "platform": "canvas",
                            "url": "https://canvas.../courses/847/discussion_topics/456",
                            "description": "Original discussion thread"
                        }
                    ],
                    "affected_students": 23,
                    "confidence_score": 0.85
                },
                "feedback_ids": [123, 124, 125],
                "created_at": "2025-09-10T08:00:00Z",
                "updated_at": "2025-09-10T09:15:00Z"
            }
        }
    }


class PriorityListResponse(BaseModel):
    """Response schema for list of priorities."""
    priorities: List[PriorityResponse] = Field(..., description="List of priority recommendations")

    model_config = {
        "json_schema_extra": {
            "example": {
                "priorities": [
                    {
                        "id": 456,
                        "course_id": "canvas_847",
                        "issue_summary": "Video quality issues affecting student comprehension",
                        "priority_score": 8,
                        "students_affected": 23,
                        "created_at": "2025-09-10T08:00:00Z"
                    }
                ]
            }
        }
    }


class PriorityRecomputeRequest(BaseModel):
    """Request schema for priority recalculation."""
    course_ids: Optional[List[str]] = Field(None, description="Specific course IDs to recompute")
    force_refresh: bool = Field(False, description="Force recalculation even if recent")

    model_config = {
        "json_schema_extra": {
            "example": {
                "course_ids": ["canvas_847", "zoho_ai_program"],
                "force_refresh": True
            }
        }
    }


class PriorityRecomputeResponse(BaseModel):
    """Response schema for priority recalculation results."""
    courses_processed: int = Field(..., description="Number of courses processed")
    priorities_updated: int = Field(..., description="Number of priorities updated")
    weight_config_used: Dict[str, float] = Field(..., description="Weight configuration used")

    model_config = {
        "json_schema_extra": {
            "example": {
                "courses_processed": 10,
                "priorities_updated": 8,
                "weight_config_used": {
                    "impact": 0.40,
                    "urgency": 0.35,
                    "effort": 0.25,
                    "strategic": 0.15,
                    "trend": 0.10
                }
            }
        }
    }


class ReviewCreateRequest(BaseModel):
    """Request schema for creating priority reviews."""
    reviewer_name: str = Field(..., description="Name of the reviewer")
    validated: bool = Field(..., description="Whether the priority is validated")
    action_taken: Optional[str] = Field(None, description="Action taken")
    notes: Optional[str] = Field(None, description="Reviewer notes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reviewer_name": "Dr. Sarah Johnson",
                "validated": True,
                "action_taken": "implemented",
                "notes": "Video quality has been upgraded. Issue resolved."
            }
        }
    }