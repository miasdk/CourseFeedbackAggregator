"""
Canvas Survey SQLAlchemy Model

Represents Canvas quizzes identified as course feedback surveys.
Hybrid approach: Canvas API field names + our business logic enhancements.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, DECIMAL, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class CanvasSurvey(Base):
    """
    Canvas quiz identified as a feedback survey.

    Stores metadata about Canvas quizzes that have been identified
    as course feedback surveys through our detection algorithm.

    Maps to Canvas Quiz API object with additional business logic fields.
    Canvas API: https://canvas.instructure.com/doc/api/quizzes.html

    Relationships:
        - Belongs to Course (many-to-one)
        - Has many StudentFeedback (one-to-many)
    """
    __tablename__ = "canvas_surveys"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    # Canvas Quiz API fields (exact naming from API)
    canvas_quiz_id = Column(Integer, nullable=False, comment="Maps to Canvas Quiz.id")
    title = Column(String(500), nullable=False, comment="Canvas Quiz.title")
    description = Column(Text, comment="Canvas Quiz.description")
    quiz_type = Column(String(50), comment="Canvas Quiz.quiz_type: 'practice_quiz', 'assignment', 'graded_survey', 'survey'")
    points_possible = Column(Integer, default=0, comment="Canvas Quiz.points_possible")
    question_count = Column(Integer, comment="Canvas Quiz.question_count")
    published = Column(Boolean, default=False, comment="Canvas Quiz.published")
    anonymous_submissions = Column(Boolean, default=False, comment="Canvas Quiz.anonymous_submissions")

    # Timing fields from Canvas API (optional)
    due_at = Column(TIMESTAMP(timezone=True), comment="Canvas Quiz.due_at")
    lock_at = Column(TIMESTAMP(timezone=True), comment="Canvas Quiz.lock_at")
    unlock_at = Column(TIMESTAMP(timezone=True), comment="Canvas Quiz.unlock_at")

    # Our business logic enhancements
    response_count = Column(Integer, default=0, comment="Count of student submissions (our calculation)")
    identification_confidence = Column(
        DECIMAL(3, 2),
        comment="Confidence score (0.00-1.00) that this quiz is a feedback survey (our algorithm)"
    )

    # Timestamps (our tracking)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_synced = Column(TIMESTAMP(timezone=True), comment="Last time we synced from Canvas API")

    # Relationships
    course = relationship("Course", back_populates="surveys")
    student_feedback = relationship(
        "StudentFeedback",
        back_populates="canvas_survey",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_canvas_surveys_course_id", "course_id"),
        Index("idx_canvas_surveys_canvas_quiz_id", "canvas_quiz_id"),
        Index("idx_canvas_surveys_confidence", "identification_confidence"),
        Index("idx_canvas_surveys_last_synced", "last_synced"),
        Index("idx_canvas_surveys_published", "published"),
        # Unique constraint: one quiz per course
        Index("uq_canvas_surveys_course_quiz", "course_id", "canvas_quiz_id", unique=True),
    )

    def __repr__(self):
        return f"<CanvasSurvey(id={self.id}, title='{self.title}', confidence={self.identification_confidence})>"

    @property
    def is_high_confidence(self) -> bool:
        """Check if survey identification confidence is high (>= 0.80)"""
        if self.identification_confidence is None:
            return False
        return float(self.identification_confidence) >= 0.80

    @property
    def is_likely_feedback(self) -> bool:
        """
        Determine if this quiz is likely a feedback survey.

        Uses multiple signals from Canvas API:
        - Quiz type indicates survey
        - Anonymous and ungraded (typical feedback pattern)
        - High confidence score from our detection algorithm
        """
        # High confidence from our detection algorithm
        if self.is_high_confidence:
            return True

        # Canvas quiz_type explicitly says it's a survey
        if self.quiz_type in ['survey', 'graded_survey']:
            return True

        # Anonymous and ungraded (typical feedback survey pattern)
        if self.anonymous_submissions and self.points_possible == 0:
            return True

        return False

    @property
    def is_active(self) -> bool:
        """
        Check if survey is currently active (published and not locked).

        Returns True if:
        - Published in Canvas
        - Not locked (lock_at is None or in the future)
        """
        if not self.published:
            return False

        # If there's no lock date, it's active
        if self.lock_at is None:
            return True

        # If locked in the future, it's still active
        from datetime import datetime, timezone
        return self.lock_at > datetime.now(timezone.utc)
