"""Configuration package for Course Feedback Aggregator."""

from .config import settings
from .database import (
    get_db,
    create_tables,
    Course,
    Feedback,
    Priority,
    Review,
    WeightConfig,
    get_active_weights
)

__all__ = [
    "settings",
    "get_db",
    "create_tables",
    "Course",
    "Feedback", 
    "Priority",
    "Review",
    "WeightConfig",
    "get_active_weights"
]