"""Controllers package for Course Feedback Aggregator.

This package implements the Controller layer of the MVC architecture,
providing clean separation between HTTP routing and business logic.

Controllers handle:
- Request validation and preprocessing
- Business logic orchestration
- Service layer coordination
- Response preparation

Each controller focuses on a specific domain area and can be easily
tested, reused across different interfaces (API, CLI, background jobs).
"""

from .base_controller import BaseController
from .feedback_controller import FeedbackController
from .priority_controller import PriorityController
from .weight_controller import WeightController
from .ingest_controller import IngestController

__all__ = [
    "BaseController",
    "FeedbackController", 
    "PriorityController",
    "WeightController",
    "IngestController"
]