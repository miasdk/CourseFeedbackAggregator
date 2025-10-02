"""
Test courses fetching with reasonable limits and progress
"""

import asyncio
from app.services.canvas import CanvasCoursesClient


async def test_limited_courses():
    """Test fetching courses with progress output"""
    print("\n" + "=" * 70)
    print("CANVAS COURSES - LIMITED TEST")
    print("=" * 70 + "\n")

    client = CanvasCoursesClient()

    try:
        # Modify the client to add progress tracking
        original_get_paginated = client._get_paginated

        async def get_paginated_with_progress(endpoint, params=None):
            """Wrapper that shows progress"""
            all_items = []
            url = f"{client.base_url}{endpoint}"

            if params is None:
                params = {}
            params.setdefault("per_page", client.per_page)

            page = 0
            max_pages = 10  # Limit for testing

            import httpx
            async with httpx.AsyncClient(timeout=client.timeout) as http_client:
                while url and page < max_pages:
                    page += 1
                    print(f"Fetching page {page}...", end=" ", flush=True)

                    response = await http_client.get(url, headers=client.headers, params=params)
                    response.raise_for_status()

                    items = response.json()
                    all_items.extend(items)

                    print(f"Got {len(items)} courses (total: {len(all_items)})")

                    url = client._get_next_page_url(response)
                    params = {}

                if url:
                    print(f"\n⚠️  Stopped at page {page} (limit reached)")
                    print(f"   More pages available, but showing first {len(all_items)} courses")
                else:
                    print(f"\n✓ Fetched all {len(all_items)} courses")

            return all_items

        # Replace method temporarily
        client._get_paginated = get_paginated_with_progress

        # Fetch courses
        courses = await client.get_all()

        print(f"\n{'=' * 70}")
        print(f"RESULT: {len(courses)} courses fetched")
        print(f"{'=' * 70}\n")

        # Show sample
        print("Sample courses:")
        for course in courses[:5]:
            print(f"  [{course.get('id')}] {course.get('name')} - {course.get('workflow_state')}")

        print(f"\n{'=' * 70}\n")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_limited_courses())
