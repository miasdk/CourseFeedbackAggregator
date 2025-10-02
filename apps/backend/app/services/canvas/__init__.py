"""
Canvas API Clients

Separated by resource for clean architecture.

Usage:
    from app.services.canvas import CanvasCoursesClient

    client = CanvasCoursesClient()
    courses = await client.get_all()
"""

from .courses import CanvasCoursesClient

# Future imports (implement when needed):
# from .quizzes import CanvasQuizzesClient
# from .submissions import CanvasSubmissionsClient

__all__ = [
    "CanvasCoursesClient",
    # "CanvasQuizzesClient",
    # "CanvasSubmissionsClient",
]
