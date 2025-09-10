"""Review model for human validation workflow."""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Review(Base):
    """Model for tracking admin review and validation of AI recommendations."""
    
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    reviewer_name = Column(String(255), nullable=False)
    validated = Column(Boolean, default=False)
    action_taken = Column(String(50))  # "implemented", "rejected", "deferred"
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to priority
    priority = relationship("Priority", back_populates="reviews")

    def __repr__(self):
        return f"<Review(priority_id={self.priority_id}, validated={self.validated}, action='{self.action_taken}')>"