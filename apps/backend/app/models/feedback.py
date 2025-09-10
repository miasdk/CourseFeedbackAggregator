"""Feedback model for storing course feedback from Canvas and Zoho."""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean
from datetime import datetime
from .base import Base


class Feedback(Base):
    """Model for unified feedback from Canvas LMS and Zoho CRM."""
    
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), index=True, nullable=False)  # "canvas_847" or "zoho_ai_program"
    course_name = Column(String(255), nullable=False)
    student_email = Column(String(255))
    student_name = Column(String(255))
    feedback_text = Column(Text)
    rating = Column(Float)  # 1-5 scale normalized
    severity = Column(String(20))  # critical/high/medium/low
    source = Column(String(10), nullable=False, index=True)  # "canvas" or "zoho"
    source_id = Column(String(100))  # Original ID for provenance
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Feedback(course_id='{self.course_id}', source='{self.source}', rating={self.rating})>"