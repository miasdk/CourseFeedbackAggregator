"""
Debug Link header parsing - see the exact format Canvas returns
"""

import asyncio
import httpx
from app.core.config import get_settings


async def debug_link_header():
    """Show full Link header from Canvas"""
    settings = get_settings()

    print("\n" + "=" * 70)
    print("LINK HEADER DEBUG")
    print("=" * 70 + "\n")

    url = f"{settings.CANVAS_BASE_URL}/api/v1/accounts/{settings.CANVAS_ACCOUNT_ID}/courses"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Page 1
        print("=== PAGE 1 ===")
        response = await client.get(url, headers=settings.canvas_headers, params={"per_page": 10})
        link = response.headers.get("Link", "")
        print(f"\nFull Link header:\n{link}\n")

        # Parse and show each link
        links = link.split(",")
        for i, link_part in enumerate(links):
            print(f"Link {i+1}: {link_part.strip()}")

        # Page 2 (extract URL from Link header)
        print("\n" + "=" * 70)
        print("=== PAGE 2 ===")

        # Get page 2 URL from Link header
        page2_url = None
        for link_part in links:
            if 'rel="next"' in link_part:
                page2_url = link_part.split(";")[0].strip().strip("<>")
                break

        if page2_url:
            print(f"\nFetching: {page2_url}\n")
            response2 = await client.get(page2_url, headers=settings.canvas_headers)
            link2 = response2.headers.get("Link", "")
            print(f"Full Link header:\n{link2}\n")

            # Parse and show each link
            links2 = link2.split(",")
            for i, link_part in enumerate(links2):
                print(f"Link {i+1}: {link_part.strip()}")

            # Check for next
            print("\n--- Parsing for 'next' ---")
            for link_part in links2:
                if 'rel="next"' in link_part:
                    next_url = link_part.split(";")[0].strip().strip("<>")
                    print(f"Found next URL: {next_url}")
                    print(f"Current URL: {page2_url}")
                    print(f"Same? {next_url == page2_url}")


if __name__ == "__main__":
    asyncio.run(debug_link_header())
