"""
Database models for Course Feedback Aggregator
Unified schema for Canvas and Zoho data with full provenance tracking
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

Base = declarative_base()

class DataSource(str, Enum):
    CANVAS = "canvas"
    ZOHO = "zoho"
    MANUAL = "manual"

class FeedbackType(str, Enum):
    REVIEW = "review"
    DISCUSSION = "discussion"
    SURVEY = "survey"
    EVALUATION = "evaluation"

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Course(Base):
    """Core course information unified from all sources"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Canvas-specific identifiers
    canvas_id = Column(Integer, unique=True, nullable=True, index=True)
    canvas_course_code = Column(String(50), nullable=True)
    
    # Zoho/External identifiers  
    external_id = Column(String(100), nullable=True)
    external_code = Column(String(50), nullable=True)
    
    # Universal course data
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    term = Column(String(50), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Instructor information
    instructor_name = Column(String(100), nullable=True)
    instructor_email = Column(String(100), nullable=True)
    
    # Enrollment data
    total_students = Column(Integer, default=0)
    active_students = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_sync_at = Column(DateTime, nullable=True)
    
    # Relationships
    feedback_items = relationship("FeedbackItem", back_populates="course")
    recommendations = relationship("Recommendation", back_populates="course")
    
    def to_dict(self):
        return {
            "id": self.id,
            "canvas_id": self.canvas_id,
            "name": self.name,
            "course_code": self.canvas_course_code or self.external_code,
            "term": self.term,
            "instructor": self.instructor_name,
            "total_students": self.total_students,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }

class FeedbackItem(Base):
    """Individual feedback entries with full provenance"""
    __tablename__ = "feedback_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    
    # Source tracking (critical for explainability)
    source = Column(SQLEnum(DataSource), nullable=False, index=True)
    source_id = Column(String(100), nullable=True)  # Original ID from source system
    source_url = Column(String(500), nullable=True)  # Direct link back to source
    
    # Feedback classification
    feedback_type = Column(SQLEnum(FeedbackType), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)  # "content", "instruction", "technology"
    
    # Content
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)  # Numeric rating if available
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    
    # Student context (anonymized)
    student_year = Column(String(20), nullable=True)
    student_major = Column(String(100), nullable=True)
    
    # Temporal data
    submitted_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Analysis results
    processed = Column(Boolean, default=False, index=True)
    issues_identified = Column(JSON, nullable=True)  # Array of identified issues
    
    # Relationships
    course = relationship("Course", back_populates="feedback_items")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_course_source', 'course_id', 'source'),
        Index('idx_submitted_processed', 'submitted_at', 'processed'),
    )
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "source": self.source,
            "source_url": self.source_url,
            "type": self.feedback_type,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "rating": self.rating,
            "sentiment_score": self.sentiment_score,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "issues": self.issues_identified
        }

class WeightConfig(Base):
    """Tunable scoring weights with version control"""
    __tablename__ = "weight_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # "default", "experimental_v2"
    description = Column(Text, nullable=True)
    
    # Scoring weights (sum should equal 1.0)
    impact_weight = Column(Float, default=0.35)      # How many students affected
    urgency_weight = Column(Float, default=0.25)     # Time sensitivity  
    effort_weight = Column(Float, default=0.20)      # Implementation difficulty
    strategic_weight = Column(Float, default=0.15)   # Institutional priorities
    trend_weight = Column(Float, default=0.05)       # Issue trajectory
    
    # Configuration metadata
    is_active = Column(Boolean, default=False, index=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="weight_config")

class Recommendation(Base):
    """Generated priority recommendations with full explainability"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    weight_config_id = Column(Integer, ForeignKey("weight_configs.id"), nullable=False)
    
    # Recommendation details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority_level = Column(SQLEnum(PriorityLevel), nullable=False, index=True)
    
    # Scoring breakdown (for explainability)
    total_score = Column(Float, nullable=False, index=True)
    impact_score = Column(Float, nullable=False)
    urgency_score = Column(Float, nullable=False)  
    effort_score = Column(Float, nullable=False)
    strategic_score = Column(Float, nullable=False)
    trend_score = Column(Float, nullable=False)
    
    # Evidence and explanation
    evidence_count = Column(Integer, default=0)  # Number of supporting feedback items
    evidence_summary = Column(JSON, nullable=True)  # Key evidence points
    explanation = Column(Text, nullable=False)  # Human-readable explanation
    
    # Implementation tracking
    status = Column(String(50), default="open", index=True)  # open, in_progress, resolved
    assigned_to = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    generated_at = Column(DateTime, server_default=func.now(), index=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="recommendations")
    weight_config = relationship("WeightConfig", back_populates="recommendations")
    
    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "priority_level": self.priority_level,
            "total_score": round(self.total_score, 2),
            "score_breakdown": {
                "impact": round(self.impact_score, 2),
                "urgency": round(self.urgency_score, 2),
                "effort": round(self.effort_score, 2),
                "strategic": round(self.strategic_score, 2),
                "trend": round(self.trend_score, 2)
            },
            "evidence_count": self.evidence_count,
            "explanation": self.explanation,
            "status": self.status,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }

class SyncLog(Base):
    """Track data synchronization from external sources"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(SQLEnum(DataSource), nullable=False, index=True)
    
    # Sync details
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running")  # running, success, failed
    
    # Results
    records_processed = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    # Error details
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "records_processed": self.records_processed,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "errors": self.errors_count
        }