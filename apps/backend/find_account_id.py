"""
Find Canvas Account ID for Executive Education

Run this to discover your account ID, then we'll use it to fetch courses.
"""

import asyncio
import httpx
from app.core.config import get_settings


async def find_accounts():
    """Find available Canvas accounts"""
    settings = get_settings()

    print("\n" + "=" * 70)
    print("FINDING CANVAS ACCOUNT IDs")
    print("=" * 70 + "\n")

    url = f"{settings.CANVAS_BASE_URL}/api/v1/accounts"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url, headers=settings.canvas_headers)
            response.raise_for_status()

            accounts = response.json()

            print(f"Found {len(accounts)} account(s):\n")

            for account in accounts:
                account_id = account.get('id')
                account_name = account.get('name')
                workflow = account.get('workflow_state', 'unknown')

                print(f"Account ID: {account_id}")
                print(f"  Name: {account_name}")
                print(f"  Status: {workflow}")
                print()

            # Try to find Executive Education account
            exec_ed = [a for a in accounts if 'executive' in a.get('name', '').lower()]
            if exec_ed:
                print("=" * 70)
                print("FOUND EXECUTIVE EDUCATION ACCOUNT:")
                print(f"  ID: {exec_ed[0]['id']}")
                print(f"  Name: {exec_ed[0]['name']}")
                print("=" * 70 + "\n")
                print(f"Add this to your .env file:")
                print(f"CANVAS_ACCOUNT_ID={exec_ed[0]['id']}")
            else:
                print("Note: Use the account ID that matches your organization")

        except Exception as e:
            print(f"ERROR: {e}")
            print("\nYour API token may not have permission to list accounts.")
            print("Try using account ID: 1 (root account)")


if __name__ == "__main__":
    asyncio.run(find_accounts())
