"""
Priority model for storing calculated priority recommendations
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Priority(Base):
    __tablename__ = "priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey('courses.course_id'), nullable=False, index=True)
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
    
    # Relationships
    course = relationship("Course", back_populates="priorities")
    reviews = relationship("Review", back_populates="priority", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Priority(course_id='{self.course_id}', score={self.priority_score}, students={self.students_affected})>"