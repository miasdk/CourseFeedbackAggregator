"""
Student Feedback Pydantic Schemas

Validation schemas for student feedback submissions and responses.
Maps Canvas QuizSubmission and QuizQuestion structures to our models.
"""
from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ===== Feedback Response Schemas =====

class FeedbackResponseBase(BaseModel):
    """Base schema for individual question/answer pair"""
    canvas_question_id: int = Field(..., description="Canvas QuizQuestion.id")
    question_name: Optional[str] = Field(None, max_length=255, description="Canvas QuizQuestion.question_name")
    question_text: str = Field(..., description="Canvas QuizQuestion.question_text")
    question_type: str = Field(..., max_length=50, description="Canvas QuizQuestion.question_type")
    points_possible: Optional[int] = Field(None, description="Canvas QuizQuestion.points_possible")

    # Student's answer (varies by question type)
    response_text: Optional[str] = Field(None, description="For essay/short answer questions")
    response_numeric: Optional[Decimal] = Field(None, description="For numerical questions and ratings")
    selected_answer_text: Optional[str] = Field(None, max_length=500, description="For multiple choice")
    selected_answer_id: Optional[int] = Field(None, description="Canvas answer ID for multiple choice")

    # Our categorization and analysis
    question_category: Optional[str] = Field(None, max_length=100, description="Our categorization")
    sentiment_score: Optional[Decimal] = Field(None, ge=-1, le=1, description="AI sentiment analysis")
    contains_improvement_suggestion: bool = Field(default=False, description="Has actionable suggestion?")
    is_critical_issue: bool = Field(default=False, description="Is this urgent/critical?")


class FeedbackResponseCreate(FeedbackResponseBase):
    """Schema for creating a new feedback response"""
    student_feedback_id: UUID = Field(..., description="Parent submission ID")


class FeedbackResponseDetail(FeedbackResponseBase):
    """Schema for feedback response API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_feedback_id: UUID
    created_at: datetime


# ===== Student Feedback Schemas =====

class StudentFeedbackBase(BaseModel):
    """Base schema for student submission"""
    canvas_submission_id: int = Field(..., description="Canvas QuizSubmission.id")
    student_canvas_id: Optional[int] = Field(None, description="Canvas user_id (NULL for anonymous)")

    # Timing
    started_at: Optional[datetime] = Field(None, description="Canvas QuizSubmission.started_at")
    finished_at: Optional[datetime] = Field(None, description="Canvas QuizSubmission.finished_at")

    # Attempt tracking
    attempt: int = Field(default=1, description="Canvas QuizSubmission.attempt")

    # Scoring (usually NULL for ungraded surveys)
    score: Optional[Decimal] = Field(None, description="Canvas QuizSubmission.score")
    kept_score: Optional[Decimal] = Field(None, description="Canvas QuizSubmission.kept_score")
    fudge_points: Optional[Decimal] = Field(None, description="Canvas QuizSubmission.fudge_points")

    # Status
    workflow_state: Optional[str] = Field(None, max_length=50, description="Canvas QuizSubmission.workflow_state")


class StudentFeedbackCreate(StudentFeedbackBase):
    """Schema for creating a new student feedback submission"""
    canvas_survey_id: UUID = Field(..., description="Survey this submission belongs to")
    course_id: int = Field(..., description="Course ID for denormalized queries")
    raw_response_data: Dict[str, Any] = Field(..., description="Full Canvas JSON response")


class StudentFeedbackResponse(StudentFeedbackBase):
    """Schema for student feedback API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    canvas_survey_id: UUID
    course_id: int
    processed_at: datetime

    # Include parsed responses
    responses: Optional[List[FeedbackResponseDetail]] = Field(None, description="Individual Q&A pairs")

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if submission is complete"""
        return self.workflow_state == "complete"

    @computed_field
    @property
    def has_critical_issues(self) -> bool:
        """Check if any responses contain critical issues"""
        if not self.responses:
            return False
        return any(r.is_critical_issue for r in self.responses)


class StudentFeedbackList(BaseModel):
    """Paginated list of student feedback submissions"""
    submissions: List[StudentFeedbackResponse]
    total: int
    skip: int
    limit: int


# ===== Course Feedback Aggregation Schemas =====

class ImprovementTheme(BaseModel):
    """Individual improvement theme with count"""
    theme: str = Field(..., description="Theme name")
    count: int = Field(..., description="Number of responses mentioning this theme")
    percentage: float = Field(..., description="Percentage of total responses")


class CourseFeedbackSummary(BaseModel):
    """Aggregated course feedback metrics for priority scoring"""
    course_id: int
    course_name: str

    # Participation metrics
    total_students: int = Field(..., description="Total enrolled students")
    total_responses: int = Field(..., description="Number of student submissions")
    response_rate: Decimal = Field(..., description="Responses / total students")

    # Rating metrics
    average_course_rating: Optional[Decimal] = Field(None, description="Average rating from numeric questions")
    rating_count: int = Field(default=0, description="Number of rating responses")

    # Issue metrics
    critical_issues_count: int = Field(default=0, description="Count of flagged critical issues")
    improvement_suggestions_count: int = Field(default=0, description="Count of improvement suggestions")

    # Theme analysis
    top_improvement_themes: List[ImprovementTheme] = Field(default=[], description="Most common themes")

    # Timing
    last_feedback_date: Optional[datetime] = Field(None, description="Most recent submission")

    # Categorized response counts
    content_responses: int = Field(default=0, description="Course content responses")
    instructor_responses: int = Field(default=0, description="Instructor responses")
    technical_responses: int = Field(default=0, description="Technical issue responses")
    assessment_responses: int = Field(default=0, description="Assessment responses")
    interaction_responses: int = Field(default=0, description="Interaction responses")

    @computed_field
    @property
    def has_sufficient_data(self) -> bool:
        """Check if we have enough responses for meaningful analysis"""
        return self.total_responses >= 5 and self.response_rate >= Decimal('0.10')

    @computed_field
    @property
    def critical_issues_ratio(self) -> Decimal:
        """Calculate ratio of critical issues to responses"""
        if self.total_responses == 0:
            return Decimal('0')
        return Decimal(str(self.critical_issues_count / self.total_responses))


class CategoryBreakdown(BaseModel):
    """Breakdown of responses by category"""
    category: str
    question_count: int
    response_count: int
    average_rating: Optional[Decimal]
    critical_issues: int


class CourseFeedbackDetail(CourseFeedbackSummary):
    """Detailed course feedback with category breakdowns"""
    category_breakdowns: List[CategoryBreakdown] = Field(default=[], description="Response breakdown by category")
    recent_submissions: List[StudentFeedbackResponse] = Field(default=[], description="Most recent submissions")


# ===== Sync Response Schemas =====

class FeedbackSyncResponse(BaseModel):
    """Response from feedback sync operation"""
    status: str
    survey_id: UUID
    course_id: int
    submissions_found: int
    submissions_stored: int
    responses_parsed: int
    critical_issues_detected: int
    timestamp: datetime
