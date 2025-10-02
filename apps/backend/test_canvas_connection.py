"""
Quick Canvas API connectivity test - diagnose connection issues
"""

import asyncio
import httpx
from app.core.config import get_settings

async def test_simple_request():
    """Test basic Canvas API connectivity"""
    settings = get_settings()

    print("\n" + "=" * 70)
    print("CANVAS API CONNECTIVITY TEST")
    print("=" * 70 + "\n")

    print(f"Testing connection to: {settings.CANVAS_BASE_URL}")
    print(f"Account ID: {settings.CANVAS_ACCOUNT_ID}")
    print(f"Timeout: {settings.CANVAS_API_TIMEOUT}s\n")

    url = f"{settings.CANVAS_BASE_URL}/api/v1/accounts/{settings.CANVAS_ACCOUNT_ID}/courses"

    print(f"Making request to: {url}")
    print("Parameters: per_page=10 (small batch for testing)\n")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:  # Short timeout
            print("Sending request...")
            response = await client.get(
                url,
                headers=settings.canvas_headers,
                params={"per_page": 10}  # Small batch
            )

            print(f"Response status: {response.status_code}")
            print(f"Response time: {response.elapsed.total_seconds():.2f}s\n")

            if response.status_code == 200:
                courses = response.json()
                print(f"SUCCESS: Received {len(courses)} courses")

                if courses:
                    print("\nFirst course:")
                    print(f"  ID: {courses[0].get('id')}")
                    print(f"  Name: {courses[0].get('name')}")
                    print(f"  Code: {courses[0].get('course_code')}")

                # Check pagination
                link_header = response.headers.get("Link")
                if link_header:
                    print(f"\nPagination: More pages available")
                else:
                    print(f"\nPagination: No more pages (all courses fetched)")
            else:
                print(f"ERROR: {response.status_code} - {response.text[:200]}")

    except httpx.TimeoutException:
        print("ERROR: Request timed out after 10 seconds")
        print("\nPossible issues:")
        print("1. Canvas server is slow/unresponsive")
        print("2. Network connectivity issue")
        print("3. Firewall blocking request")

    except httpx.ConnectError as e:
        print(f"ERROR: Could not connect - {e}")
        print("\nCheck:")
        print("1. CANVAS_BASE_URL is correct")
        print("2. Internet connection working")

    except Exception as e:
        print(f"ERROR: {e}")

    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_simple_request())
