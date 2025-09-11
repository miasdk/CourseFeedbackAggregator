"""
Course model for storing course information from Canvas and Zoho
"""

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(String(50), primary_key=True, index=True)  # "canvas_847", "zoho_ai_program"
    course_name = Column(String(255), nullable=False)
    instructor_name = Column(String(255))
    canvas_id = Column(String(100), unique=True, index=True)
    zoho_program_id = Column(String(100), unique=True, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default='active')  # active/completed/archived
    course_metadata = Column(JSON)  # Additional course info
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="course")
    priorities = relationship("Priority", back_populates="course")

    def __repr__(self):
        return f"<Course(course_id='{self.course_id}', name='{self.course_name}', status='{self.status}')>"