"""
Feedback model for storing student feedback from Canvas and Zoho
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey('courses.course_id'), index=True, nullable=False)
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
    
    # Relationship back to course
    course = relationship("Course", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback(course_id='{self.course_id}', source='{self.source}', rating={self.rating})>"