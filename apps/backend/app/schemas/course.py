"""
Course Pydantic Schemas

Request/Response validation schemas for Course API endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field


class CourseBase(BaseModel):
    """Base course schema with common fields"""
    name: str = Field(..., description="Course name")
    course_code: Optional[str] = Field(None, description="Course code (e.g., LEAD101)")
    workflow_state: str = Field(..., description="Canvas workflow state (available, completed, deleted)")
    start_date: Optional[datetime] = Field(None, description="Course start date")
    end_date: Optional[datetime] = Field(None, description="Course end date")
    total_students: Optional[int] = Field(None, description="Total enrolled students")
    enrollment_term_id: Optional[int] = Field(None, description="Canvas enrollment term ID")


class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    canvas_id: int = Field(..., description="Canvas course ID")


class CourseUpdate(BaseModel):
    """Schema for updating course fields"""
    name: Optional[str] = None
    course_code: Optional[str] = None
    workflow_state: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_students: Optional[int] = None
    enrollment_term_id: Optional[int] = None


class CourseResponse(CourseBase):
    """
    Schema for course API responses

    Includes computed is_active field based on filtering logic.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Database ID")
    canvas_id: int = Field(..., description="Canvas course ID")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Determine if course is active based on naming patterns and workflow state.

        Filtering criteria from PDF analysis:
        - Exclude courses with "OLD -", "CLOSED -", "COURSE CLOSED" in name
        - Only include workflow_state: 'available' or 'unpublished'
        """
        if not self.name or not self.workflow_state:
            return False

        # Check for inactive naming patterns
        inactive_patterns = ['OLD -', 'CLOSED -', 'COURSE CLOSED']
        name_upper = self.name.upper()
        if any(pattern in name_upper for pattern in inactive_patterns):
            return False

        # Only available/unpublished courses are active
        if self.workflow_state not in ['available', 'unpublished']:
            return False

        return True


class CourseListResponse(BaseModel):
    """Schema for paginated course list responses"""
    courses: list[CourseResponse] = Field(..., description="List of courses")
    total: int = Field(..., description="Total number of courses")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(100, description="Number of items per page")

    @computed_field
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


class CourseSyncRequest(BaseModel):
    """Schema for course sync requests"""
    force_refresh: bool = Field(False, description="Force refresh all courses from Canvas")
    include_inactive: bool = Field(False, description="Include inactive courses in sync")


class CourseSyncResponse(BaseModel):
    """Schema for course sync responses"""
    status: str = Field(..., description="Sync status (success, partial, failed)")
    courses_synced: int = Field(..., description="Number of courses synced")
    courses_created: int = Field(..., description="Number of new courses created")
    courses_updated: int = Field(..., description="Number of existing courses updated")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    sync_duration_seconds: float = Field(..., description="Time taken for sync operation")
