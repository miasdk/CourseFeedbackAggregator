"""
Course Model

Represents Canvas course data with filtering support for active/inactive courses.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index, func
from sqlalchemy.orm import column_property
from sqlalchemy.sql import case
from app.core.database import Base


class Course(Base):
    """
    Canvas Course Model

    Stores all courses from Canvas API with filtering capabilities.
    Courses marked as OLD, CLOSED, or with non-available workflow_state
    are stored but can be filtered out at query time.
    """
    __tablename__ = "courses"

    # Primary Keys
    id = Column(Integer, primary_key=True, autoincrement=True)
    canvas_id = Column(Integer, unique=True, nullable=False, index=True)

    # Course Information
    name = Column(String(255), nullable=False)
    course_code = Column(String(100))
    workflow_state = Column(String(50), index=True)  # 'available', 'completed', 'deleted', etc.

    # Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Canvas Metadata
    total_students = Column(Integer)
    enrollment_term_id = Column(Integer)

    # Audit Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Course(id={self.id}, canvas_id={self.canvas_id}, name='{self.name}', workflow_state='{self.workflow_state}')>"

    @property
    def is_active(self) -> bool:
        """
        Determine if course is active based on naming patterns and workflow state.

        Inactive patterns from PDF analysis:
        - "OLD -" prefix
        - "CLOSED -" prefix
        - "COURSE CLOSED" prefix
        - workflow_state not in ['available', 'unpublished']
        """
        if not self.name or not self.workflow_state:
            return False

        # Check for inactive naming patterns
        inactive_patterns = ['OLD -', 'CLOSED -', 'COURSE CLOSED']
        name_upper = self.name.upper()
        if any(pattern in name_upper for pattern in inactive_patterns):
            return False

        # Only include courses that are available or unpublished
        if self.workflow_state not in ['available', 'unpublished']:
            return False

        return True


# Indexes for performance
Index('idx_courses_workflow_state', Course.workflow_state)
Index('idx_courses_active_lookup', Course.workflow_state, Course.name)
Index('idx_courses_canvas_id', Course.canvas_id, unique=True)
