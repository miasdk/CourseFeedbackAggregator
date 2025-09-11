"""
WeightConfig model for storing tunable scoring weights
"""

from sqlalchemy import Column, Integer, Float, DateTime, String, Boolean
from datetime import datetime
from .base import Base


class WeightConfig(Base):
    __tablename__ = "weight_configs"
    
    id = Column(Integer, primary_key=True)
    impact_weight = Column(Float, default=0.40, nullable=False)  # Student impact focus
    urgency_weight = Column(Float, default=0.35, nullable=False)  # Time-sensitive issues
    effort_weight = Column(Float, default=0.25, nullable=False)  # Quick wins preference
    strategic_weight = Column(Float, default=0.15, nullable=False)  # Course goal alignment
    trend_weight = Column(Float, default=0.10, nullable=False)  # Issue trajectory
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))  # Admin who changed weights
    is_active = Column(Boolean, default=True)  # Only one active config at a time

    def __repr__(self):
        return f"<WeightConfig(impact={self.impact_weight}, urgency={self.urgency_weight}, effort={self.effort_weight})>"
