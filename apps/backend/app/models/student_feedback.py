"""
Student Feedback SQLAlchemy Model

Represents student quiz submissions from Canvas.
Hybrid approach: Canvas API field names + our business logic enhancements.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class StudentFeedback(Base):
    """
    Student feedback submission from Canvas quiz.

    Stores student quiz submissions extracted from Canvas API.
    Maps to Canvas QuizSubmission API object with additional context.
    Canvas API: https://canvas.instructure.com/doc/api/quiz_submissions.html

    Relationships:
        - Belongs to CanvasSurvey (many-to-one)
        - Belongs to Course (many-to-one)
        - Has many FeedbackResponse (one-to-many)
    """
    __tablename__ = "student_feedback"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    canvas_survey_id = Column(
        UUID(as_uuid=True),
        ForeignKey("canvas_surveys.id", ondelete="CASCADE"),
        nullable=False
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        comment="Denormalized for query performance"
    )

    # Canvas QuizSubmission API fields (exact naming from API)
    canvas_submission_id = Column(Integer, nullable=False, comment="Maps to Canvas QuizSubmission.id")
    student_canvas_id = Column(Integer, comment="Maps to Canvas QuizSubmission.user_id (NULL for anonymous)")

    # Timing fields from Canvas API
    started_at = Column(TIMESTAMP(timezone=True), comment="Canvas QuizSubmission.started_at")
    finished_at = Column(TIMESTAMP(timezone=True), comment="Canvas QuizSubmission.finished_at")

    # Attempt tracking
    attempt = Column(Integer, default=1, comment="Canvas QuizSubmission.attempt")

    # Scoring fields from Canvas API
    score = Column(DECIMAL(10, 2), comment="Canvas QuizSubmission.score")
    kept_score = Column(DECIMAL(10, 2), comment="Canvas QuizSubmission.kept_score (final recorded score)")
    fudge_points = Column(DECIMAL(10, 2), comment="Canvas QuizSubmission.fudge_points (manual adjustment)")

    # Status tracking
    workflow_state = Column(
        String(50),
        comment="Canvas QuizSubmission.workflow_state: 'untaken', 'pending_review', 'complete', 'settings_only', 'preview'"
    )

    # Raw Canvas data for audit trail
    raw_response_data = Column(
        JSONB,
        nullable=False,
        comment="Full Canvas QuizSubmission JSON response (audit trail)"
    )

    # Our business logic enhancements
    processed_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        comment="When we processed this submission (our tracking)"
    )

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    canvas_survey = relationship("CanvasSurvey", back_populates="student_feedback")
    course = relationship("Course")
    responses = relationship(
        "FeedbackResponse",
        back_populates="student_feedback",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_student_feedback_survey_id", "canvas_survey_id"),
        Index("idx_student_feedback_course_id", "course_id"),
        Index("idx_student_feedback_student_id", "student_canvas_id"),
        Index("idx_student_feedback_workflow_state", "workflow_state"),
        Index("idx_student_feedback_finished_at", "finished_at"),
        # Unique constraint: one submission per student per survey
        # NOTE: CSV data uses student_canvas_id since canvas_submission_id is NULL for surveys
        Index(
            "uq_student_feedback_student",
            "canvas_survey_id",
            "student_canvas_id",
            unique=True
        ),
    )

    def __repr__(self):
        student_id = self.student_canvas_id or "anonymous"
        return f"<StudentFeedback(id={self.id}, student={student_id}, state='{self.workflow_state}')>"

    @property
    def is_complete(self) -> bool:
        """Check if submission is complete"""
        return self.workflow_state == "complete"

    @property
    def is_anonymous(self) -> bool:
        """Check if this is an anonymous submission"""
        return self.student_canvas_id is None

    @property
    def time_spent_minutes(self) -> int:
        """
        Calculate time spent on quiz in minutes.

        Returns:
            Minutes between started_at and finished_at, or 0 if not available
        """
        if not self.started_at or not self.finished_at:
            return 0

        delta = self.finished_at - self.started_at
        return int(delta.total_seconds() / 60)

    @property
    def final_score(self) -> float:
        """
        Get final score (kept_score if available, otherwise score).

        Returns:
            Final recorded score, or 0.0 if not graded
        """
        if self.kept_score is not None:
            return float(self.kept_score)
        elif self.score is not None:
            return float(self.score)
        return 0.0
