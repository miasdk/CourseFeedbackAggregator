"""
Canvas API Base Client - Shared HTTP functionality

This base class provides common functionality for all Canvas API clients:
- Authentication (Bearer token)
- HTTP client configuration
- Pagination handling
- Error handling

All specific Canvas clients (Courses, Quizzes, Submissions) inherit from this.
"""

import httpx
from typing import Optional, Dict, List, Any
from ...core.config import get_settings


class CanvasBaseClient:
    """
    Base client for Canvas LMS API.

    Provides shared functionality for all Canvas API clients.
    All specific resource clients (Courses, Quizzes, etc.) inherit from this.

    Key Features:
    - Authentication via Bearer token
    - Automatic pagination handling
    - Consistent error handling
    - HTTP timeout configuration
    """

    def __init__(self):
        """Initialize base client with settings from config"""
        self.settings = get_settings()
        self.base_url = self.settings.CANVAS_BASE_URL
        self.headers = self.settings.canvas_headers
        self.timeout = self.settings.CANVAS_API_TIMEOUT
        self.per_page = self.settings.CANVAS_PER_PAGE

    def _get_next_page_url(self, response: httpx.Response) -> Optional[str]:
        """
        Extract next page URL from Canvas Link header.

        Canvas API uses RFC 5988 Link headers for pagination:
        Link: <https://canvas.com/api/v1/courses?page=2>; rel="next"

        Args:
            response: HTTP response from Canvas API

        Returns:
            Next page URL or None if no more pages
        """
        link_header = response.headers.get("Link")
        if not link_header:
            return None

        # Parse Link header: <url>; rel="next", <url>; rel="first"
        links = link_header.split(",")
        for link in links:
            if 'rel="next"' in link:
                # Extract URL from <url>; rel="next"
                url = link.split(";")[0].strip().strip("<>")
                return url

        return None

    async def _get_paginated(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Fetch all pages from a paginated Canvas API endpoint.

        Automatically handles pagination by following Link headers.

        Args:
            endpoint: API endpoint path (e.g., "/api/v1/courses")
            params: Query parameters

        Returns:
            Complete list of all items across all pages

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        all_items = []
        url = f"{self.base_url}{endpoint}"

        # Set default pagination parameters
        if params is None:
            params = {}
        params.setdefault("per_page", self.per_page)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while url:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()  # Raise exception for 4xx/5xx

                items = response.json()
                all_items.extend(items)

                # Check for next page
                url = self._get_next_page_url(response)
                params = {}  # Clear params (next page URL has them)

        return all_items

    async def _get_single(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fetch a single resource from Canvas API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Single resource as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails (e.g., 404 Not Found)
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
