"""
Test pagination logic - debug what's happening in the loop
"""

import asyncio
import httpx
from app.core.config import get_settings


async def test_pagination_debug():
    """Test pagination with debug output"""
    settings = get_settings()

    print("\n" + "=" * 70)
    print("PAGINATION DEBUG TEST")
    print("=" * 70 + "\n")

    url = f"{settings.CANVAS_BASE_URL}/api/v1/accounts/{settings.CANVAS_ACCOUNT_ID}/courses"
    params = {"per_page": 10}
    all_courses = []
    page_count = 0
    max_pages = 5  # Safety limit

    async with httpx.AsyncClient(timeout=10.0) as client:
        while url and page_count < max_pages:
            page_count += 1
            print(f"\n--- PAGE {page_count} ---")
            print(f"URL: {url[:80]}...")
            print(f"Params: {params}")

            response = await client.get(url, headers=settings.canvas_headers, params=params)

            print(f"Status: {response.status_code}")

            courses = response.json()
            all_courses.extend(courses)
            print(f"Courses on this page: {len(courses)}")
            print(f"Total courses so far: {len(all_courses)}")

            # Check Link header
            link_header = response.headers.get("Link")
            if link_header:
                print(f"\nLink header found:")
                print(f"  {link_header[:150]}...")

                # Parse next URL
                links = link_header.split(",")
                next_url = None
                for link in links:
                    if 'rel="next"' in link:
                        next_url = link.split(";")[0].strip().strip("<>")
                        print(f"\nNext URL found:")
                        print(f"  {next_url[:80]}...")
                        break

                if next_url == url:
                    print("\n⚠️  WARNING: Next URL is same as current URL - INFINITE LOOP!")
                    break

                url = next_url
                params = {}  # Clear params for next page
            else:
                print("\nNo Link header - end of pages")
                url = None

        print(f"\n{'=' * 70}")
        print(f"TOTAL PAGES: {page_count}")
        print(f"TOTAL COURSES: {len(all_courses)}")
        print(f"{'=' * 70}\n")


if __name__ == "__main__":
    asyncio.run(test_pagination_debug())
