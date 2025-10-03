"""
Quiz/Survey Pydantic Schemas

Validation schemas for Canvas quiz/survey API requests and responses.
Aligned with Canvas API structure and our database models.
"""
from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ===== Canvas Survey Schemas =====

class CanvasSurveyBase(BaseModel):
    """Base schema for Canvas survey (shared fields)"""
    title: str = Field(..., max_length=500, description="Canvas Quiz.title")
    description: Optional[str] = Field(None, description="Canvas Quiz.description")
    quiz_type: Optional[str] = Field(None, max_length=50, description="Canvas Quiz.quiz_type")
    points_possible: Optional[int] = Field(default=0, description="Canvas Quiz.points_possible")
    question_count: Optional[int] = Field(None, description="Canvas Quiz.question_count")
    published: bool = Field(default=False, description="Canvas Quiz.published")
    anonymous_submissions: bool = Field(default=False, description="Canvas Quiz.anonymous_submissions")

    # Timing fields (optional)
    due_at: Optional[datetime] = Field(None, description="Canvas Quiz.due_at")
    lock_at: Optional[datetime] = Field(None, description="Canvas Quiz.lock_at")
    unlock_at: Optional[datetime] = Field(None, description="Canvas Quiz.unlock_at")


class CanvasSurveyCreate(CanvasSurveyBase):
    """Schema for creating a new survey (from Canvas sync)"""
    course_id: int = Field(..., description="Database course ID")
    canvas_quiz_id: int = Field(..., description="Canvas Quiz.id")
    identification_confidence: Optional[Decimal] = Field(None, ge=0, le=1, description="Survey detection confidence (0.00-1.00)")


class CanvasSurveyResponse(CanvasSurveyBase):
    """Schema for survey API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: int
    canvas_quiz_id: int
    response_count: int = Field(default=0, description="Number of student submissions")
    identification_confidence: Optional[Decimal] = Field(None, description="Survey detection confidence")
    created_at: datetime
    last_synced: Optional[datetime]

    @computed_field
    @property
    def is_high_confidence(self) -> bool:
        """Check if survey identification confidence is high (>= 0.80)"""
        if self.identification_confidence is None:
            return False
        return float(self.identification_confidence) >= 0.80

    @computed_field
    @property
    def is_likely_feedback(self) -> bool:
        """Determine if this quiz is likely a feedback survey"""
        # High confidence from detection algorithm
        if self.is_high_confidence:
            return True

        # Canvas quiz_type explicitly says it's a survey
        if self.quiz_type in ['survey', 'graded_survey']:
            return True

        # Anonymous and ungraded (typical feedback pattern)
        if self.anonymous_submissions and self.points_possible == 0:
            return True

        return False


class CanvasSurveyList(BaseModel):
    """Paginated list of surveys"""
    surveys: list[CanvasSurveyResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ===== Student Feedback (Quiz Submission) Schemas =====

class StudentFeedbackBase(BaseModel):
    """Base schema for student feedback (shared fields)"""
    started_at: Optional[datetime] = Field(None, description="Canvas QuizSubmission.started_at")
    finished_at: Optional[datetime] = Field(None, description="Canvas QuizSubmission.finished_at")
    attempt: int = Field(default=1, description="Canvas QuizSubmission.attempt")
    score: Optional[Decimal] = Field(None, description="Canvas QuizSubmission.score")
    kept_score: Optional[Decimal] = Field(None, description="Canvas QuizSubmission.kept_score")
    workflow_state: Optional[str] = Field(None, max_length=50, description="Canvas QuizSubmission.workflow_state")


class StudentFeedbackCreate(StudentFeedbackBase):
    """Schema for creating student feedback (from Canvas sync)"""
    canvas_survey_id: UUID
    course_id: int
    canvas_submission_id: int
    student_canvas_id: Optional[int] = Field(None, description="NULL for anonymous submissions")
    raw_response_data: dict = Field(..., description="Full Canvas QuizSubmission JSON")


class StudentFeedbackResponse(StudentFeedbackBase):
    """Schema for student feedback API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    canvas_survey_id: UUID
    course_id: int
    canvas_submission_id: int
    student_canvas_id: Optional[int]
    fudge_points: Optional[Decimal]
    processed_at: datetime
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if submission is complete"""
        return self.workflow_state == "complete"

    @computed_field
    @property
    def is_anonymous(self) -> bool:
        """Check if this is an anonymous submission"""
        return self.student_canvas_id is None

    @computed_field
    @property
    def final_score(self) -> float:
        """Get final score (kept_score if available, otherwise score)"""
        if self.kept_score is not None:
            return float(self.kept_score)
        elif self.score is not None:
            return float(self.score)
        return 0.0


class StudentFeedbackList(BaseModel):
    """Paginated list of student feedback"""
    submissions: list[StudentFeedbackResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ===== Feedback Response (Question Answer) Schemas =====

class FeedbackResponseBase(BaseModel):
    """Base schema for feedback response (shared fields)"""
    question_name: Optional[str] = Field(None, max_length=255, description="Canvas QuizQuestion.question_name")
    question_text: str = Field(..., description="Canvas QuizQuestion.question_text")
    question_type: Optional[str] = Field(None, max_length=50, description="Canvas QuizQuestion.question_type")
    points_possible: Optional[int] = Field(None, description="Canvas QuizQuestion.points_possible")

    # Student's answer (varies by question type)
    response_text: Optional[str] = Field(None, description="For essay/short answer")
    response_numeric: Optional[Decimal] = Field(None, description="For numerical/rating questions")
    selected_answer_text: Optional[str] = Field(None, max_length=500, description="For multiple choice")
    selected_answer_id: Optional[int] = Field(None, description="Canvas answer ID")


class FeedbackResponseCreate(FeedbackResponseBase):
    """Schema for creating feedback response (from Canvas sync)"""
    student_feedback_id: UUID
    canvas_question_id: int
    question_category: Optional[str] = Field(None, max_length=100, description="Our categorization")
    contains_improvement_suggestion: bool = Field(default=False)
    is_critical_issue: bool = Field(default=False)


class FeedbackResponseResponse(FeedbackResponseBase):
    """Schema for feedback response API responses"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_feedback_id: UUID
    canvas_question_id: int
    question_category: Optional[str]
    sentiment_score: Optional[Decimal]
    contains_improvement_suggestion: bool
    is_critical_issue: bool
    created_at: datetime

    @computed_field
    @property
    def is_text_response(self) -> bool:
        """Check if this is a text-based response"""
        return self.question_type in [
            'essay_question',
            'short_answer_question',
            'fill_in_multiple_blanks_question'
        ]

    @computed_field
    @property
    def is_actionable(self) -> bool:
        """Check if this response contains actionable feedback"""
        if self.contains_improvement_suggestion or self.is_critical_issue:
            return True

        # Text responses often contain actionable feedback
        if self.is_text_response and self.response_text and len(self.response_text) > 20:
            return True

        return False

    @computed_field
    @property
    def answer_preview(self) -> str:
        """Get preview of student's answer (first 100 chars)"""
        if self.response_text:
            return self.response_text[:100] + "..." if len(self.response_text) > 100 else self.response_text
        elif self.selected_answer_text:
            return self.selected_answer_text
        elif self.response_numeric is not None:
            return str(self.response_numeric)
        return "[No response]"


class FeedbackResponseList(BaseModel):
    """Paginated list of feedback responses"""
    responses: list[FeedbackResponseResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ===== Survey Statistics Schema =====

class SurveyStatistics(BaseModel):
    """Aggregated statistics for a survey"""
    survey_id: UUID
    course_id: int
    total_responses: int
    complete_responses: int
    anonymous_responses: int
    average_score: Optional[float]
    response_rate: Optional[float] = Field(None, description="responses / total_students")

    # Response categorization counts
    text_responses_count: int = 0
    critical_issues_count: int = 0
    improvement_suggestions_count: int = 0

    # Category breakdown
    category_breakdown: dict[str, int] = Field(default_factory=dict)
