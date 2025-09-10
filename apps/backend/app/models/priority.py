"""Priority model for AI-generated course improvement recommendations."""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Priority(Base):
    """Model for computed priority recommendations with explainable scoring."""
    
    __tablename__ = "priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), nullable=False, index=True)
    issue_summary = Column(Text, nullable=False)
    priority_score = Column(Integer, nullable=False)  # 1-5 scale
    impact_score = Column(Float, nullable=False)  # 1-5
    urgency_score = Column(Float, nullable=False)  # 1-5
    effort_score = Column(Float, nullable=False)  # 1-5
    strategic_score = Column(Float, default=3.0)  # 1-5
    trend_score = Column(Float, default=3.0)  # 1-5
    students_affected = Column(Integer, default=0)
    feedback_ids = Column(JSON)  # Array of contributing feedback IDs
    evidence = Column(JSON)  # Student quotes and source links
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to reviews
    reviews = relationship("Review", back_populates="priority", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Priority(course_id='{self.course_id}', score={self.priority_score}, students={self.students_affected})>"