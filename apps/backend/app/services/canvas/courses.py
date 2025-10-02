"""
Canvas Courses API Client

Handles all course-related Canvas API operations.

Official Canvas API Endpoints:
- GET /api/v1/accounts/:account_id/courses (list courses in account)
- GET /api/v1/courses/:id (get single course)

Documentation:
- Accounts: https://canvas.instructure.com/doc/api/accounts.html
- Courses: https://canvas.instructure.com/doc/api/courses.html
"""

from typing import List, Dict, Any
from .base import CanvasBaseClient


class CanvasCoursesClient(CanvasBaseClient):
    """
    Client for Canvas Courses API.

    Provides methods to interact with Canvas courses:
    - List all courses (with pagination)
    - Get single course by ID

    Example usage:
        client = CanvasCoursesClient()
        courses = await client.get_all()
        course = await client.get_by_id(123)
    """

    async def get_all(self, include: List[str] = None, account_id: int = None) -> List[Dict[str, Any]]:
        """
        Fetch all courses from Canvas account.

        Uses pagination to retrieve complete list of courses.

        Official API: GET /api/v1/accounts/:account_id/courses

        Args:
            include: Optional list of additional data to include
                    (e.g., ['total_students', 'teachers', 'term'])
            account_id: Canvas account ID (defaults to CANVAS_ACCOUNT_ID from settings)

        Returns:
            List of course dictionaries

        Example response:
            [
                {
                    "id": 123,
                    "name": "Leadership Development",
                    "course_code": "LEAD101",
                    "workflow_state": "available",
                    "start_at": "2024-01-15T00:00:00Z",
                    "end_at": "2024-05-15T00:00:00Z",
                    "enrollment_term_id": 1
                },
                ...
            ]
        """
        # Use provided account_id or default from settings
        if account_id is None:
            account_id = self.settings.CANVAS_ACCOUNT_ID

        endpoint = f"/api/v1/accounts/{account_id}/courses"
        params = {}

        if include:
            params["include[]"] = include

        return await self._get_paginated(endpoint, params)

    async def get_by_id(self, course_id: int, include: List[str] = None) -> Dict[str, Any]:
        """
        Fetch a single course by ID.

        Official API: GET /api/v1/courses/:id

        Args:
            course_id: Canvas course ID
            include: Optional list of additional data to include

        Returns:
            Single course dictionary

        Raises:
            httpx.HTTPStatusError: If course not found (404)

        Example response:
            {
                "id": 123,
                "name": "Leadership Development",
                "course_code": "LEAD101",
                "workflow_state": "available",
                ...
            }
        """
        endpoint = f"/api/v1/courses/{course_id}"
        params = {}

        if include:
            params["include[]"] = include

        return await self._get_single(endpoint, params)


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_courses_client():
        """Test Canvas Courses API client"""
        print("\n" + "=" * 70)
        print("CANVAS COURSES API CLIENT TEST")
        print("=" * 70 + "\n")

        client = CanvasCoursesClient()

        try:
            # Test 1: Fetch all courses (with limit for testing)
            print(f"TEST 1: Fetching courses from account {client.settings.CANVAS_ACCOUNT_ID}...")
            print("Note: Limiting to first 200 courses for testing\n")

            # Fetch with progress
            all_courses = []
            page = 0
            max_pages = 20  # Reasonable limit for testing

            import httpx
            async with httpx.AsyncClient(timeout=client.timeout) as http_client:
                url = f"{client.base_url}/api/v1/accounts/{client.settings.CANVAS_ACCOUNT_ID}/courses"
                params = {"per_page": 10}  # Small pages for visible progress

                while url and page < max_pages:
                    page += 1
                    print(f"  Page {page}...", end=" ", flush=True)

                    response = await http_client.get(url, headers=client.headers, params=params)
                    response.raise_for_status()

                    courses_batch = response.json()
                    all_courses.extend(courses_batch)
                    print(f"{len(courses_batch)} courses (total: {len(all_courses)})")

                    url = client._get_next_page_url(response)
                    params = {}

            courses = all_courses
            print(f"\nSUCCESS: Found {len(courses)} courses")
            print(f"API: GET /api/v1/accounts/{client.settings.CANVAS_ACCOUNT_ID}/courses")
            print(f"Pagination: Fetched {page} pages\n")

            # Show first 5 courses
            print("Sample courses:")
            for course in courses[:5]:
                course_id = course.get('id')
                course_name = course.get('name', 'Unnamed')
                course_code = course.get('course_code', 'No code')
                workflow = course.get('workflow_state', 'unknown')
                print(f"  [{course_id}] {course_name} ({course_code}) - {workflow}")

            if len(courses) > 5:
                print(f"  ... and {len(courses) - 5} more courses\n")

            # Test 2: Fetch single course
            if courses:
                print("TEST 2: Fetching single course...")
                first_course_id = courses[0]['id']
                course = await client.get_by_id(first_course_id)
                print(f"SUCCESS: Retrieved course '{course.get('name')}'\n")

                # Show available fields
                print("Available course data fields:")
                for key in list(course.keys())[:12]:
                    value = str(course[key])[:50]
                    print(f"  - {key}: {value}")

            print("\n" + "=" * 70)
            print("SUCCESS: All Canvas Courses API tests passed!")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"ERROR: {e}")
            print("\nTroubleshooting:")
            print("1. Verify CANVAS_API_TOKEN in .env")
            print("2. Verify CANVAS_BASE_URL in .env")
            print("3. Check Canvas API token permissions")
            print("4. Check internet connection")
            raise

    asyncio.run(test_courses_client())
