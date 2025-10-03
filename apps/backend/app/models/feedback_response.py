"""
Feedback Response SQLAlchemy Model

Represents individual question answers from Canvas quiz submissions.
Hybrid approach: Canvas API field names + our business logic enhancements.
"""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class FeedbackResponse(Base):
    """
    Individual question response from student feedback.

    Stores answers to individual quiz questions from Canvas submissions.
    Maps to Canvas QuizQuestion API object with student's answer.
    Canvas API: https://canvas.instructure.com/doc/api/quiz_questions.html

    Relationships:
        - Belongs to StudentFeedback (many-to-one)
    """
    __tablename__ = "feedback_responses"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    student_feedback_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_feedback.id", ondelete="CASCADE"),
        nullable=False
    )

    # Canvas QuizQuestion API fields (exact naming from API)
    canvas_question_id = Column(Integer, nullable=False, comment="Maps to Canvas QuizQuestion.id")
    question_name = Column(String(255), comment="Canvas QuizQuestion.question_name")
    question_text = Column(Text, nullable=False, comment="Canvas QuizQuestion.question_text")
    question_type = Column(
        String(50),
        comment="""Canvas QuizQuestion.question_type:
        'essay_question', 'multiple_choice_question', 'multiple_answers_question',
        'true_false_question', 'short_answer_question', 'numerical_question',
        'matching_question', 'fill_in_multiple_blanks_question', 'text_only_question'"""
    )
    points_possible = Column(Integer, comment="Canvas QuizQuestion.points_possible")

    # Student's answer (different fields based on question_type)
    response_text = Column(Text, comment="For essay/short answer questions")
    response_numeric = Column(DECIMAL(10, 2), comment="For numerical questions and ratings")
    selected_answer_text = Column(String(500), comment="For multiple choice/true-false questions")
    selected_answer_id = Column(Integer, comment="Canvas answer ID for multiple choice")

    # Our business logic enhancements - Question categorization
    question_category = Column(
        String(100),
        comment="""Our categorization: 'course_content', 'instructor', 'technical',
        'overall_satisfaction', 'assessment', 'interaction', 'other'"""
    )

    # Our business logic enhancements - Content analysis
    sentiment_score = Column(
        DECIMAL(3, 2),
        comment="AI sentiment analysis score (-1.00 to 1.00, future enhancement)"
    )
    contains_improvement_suggestion = Column(
        Boolean,
        default=False,
        comment="Our analysis: Does this response suggest an improvement?"
    )
    is_critical_issue = Column(
        Boolean,
        default=False,
        comment="Our analysis: Is this a critical/urgent issue?"
    )

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    student_feedback = relationship("StudentFeedback", back_populates="responses")

    # Indexes for performance
    __table_args__ = (
        Index("idx_feedback_responses_student_feedback_id", "student_feedback_id"),
        Index("idx_feedback_responses_category", "question_category"),
        Index("idx_feedback_responses_critical", "is_critical_issue"),
        Index("idx_feedback_responses_improvement", "contains_improvement_suggestion"),
        Index("idx_feedback_responses_question_type", "question_type"),
    )

    def __repr__(self):
        preview = (self.response_text or self.selected_answer_text or str(self.response_numeric) or "")[:50]
        return f"<FeedbackResponse(id={self.id}, type='{self.question_type}', response='{preview}...')>"

    @property
    def is_text_response(self) -> bool:
        """Check if this is a text-based response (essay, short answer)"""
        return self.question_type in [
            'essay_question',
            'short_answer_question',
            'fill_in_multiple_blanks_question'
        ]

    @property
    def is_rating_response(self) -> bool:
        """Check if this is a rating/numerical response"""
        return self.question_type in [
            'numerical_question',
            'multiple_choice_question',  # Often used for ratings (1-5)
        ]

    @property
    def is_actionable(self) -> bool:
        """
        Check if this response contains actionable feedback.

        Returns True if:
        - Contains improvement suggestion
        - Is a critical issue
        - Is a text response (likely contains detailed feedback)
        """
        if self.contains_improvement_suggestion or self.is_critical_issue:
            return True

        # Text responses often contain actionable feedback
        if self.is_text_response and self.response_text and len(self.response_text) > 20:
            return True

        return False

    def get_answer_value(self) -> str:
        """
        Get the student's answer regardless of question type.

        Returns:
            String representation of the answer
        """
        if self.response_text:
            return self.response_text
        elif self.selected_answer_text:
            return self.selected_answer_text
        elif self.response_numeric is not None:
            return str(self.response_numeric)
        else:
            return "[No response]"
