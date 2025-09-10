"""Course model for unified course information and mapping."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .base import Base


class Course(Base):
    """Model for unified course information with Canvas/Zoho ID mapping."""
    
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    canvas_id = Column(String(50), nullable=False, unique=True, index=True)
    zoho_id = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    course_code = Column(String(50))
    account_id = Column(Integer)
    workflow_state = Column(String(20))  # active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    enrollment_term_id = Column(Integer)
    total_students = Column(Integer)
    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime)
    canvas_uuid = Column(String(100))
    default_view = Column(String(50))
    time_zone = Column(String(50))

    def __repr__(self):
        return f"<Course(canvas_id='{self.canvas_id}', name='{self.name}', state='{self.workflow_state}')>"