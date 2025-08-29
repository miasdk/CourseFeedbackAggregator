#!/usr/bin/env python
"""
Debug Canvas API Connection
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def debug_canvas_connection():
    """Debug Canvas API connection step by step"""
    
    token = os.getenv('CANVAS_API_TOKEN')
    url = os.getenv('CANVAS_API_URL', 'https://usfca.instructure.com')
    
    print("=" * 60)
    print("CANVAS API DEBUG")
    print("=" * 60)
    
    print(f"Token (first 20 chars): {token[:20]}...")
    print(f"Token (last 10 chars): ...{token[-10:]}")
    print(f"Token length: {len(token)}")
    print(f"Canvas URL: {url}")
    
    # Try different header formats
    headers_to_try = [
        {'Authorization': f'Bearer {token}'},
        {'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
        {'Authorization': f'Bearer {token}', 'Accept': 'application/json+canvas-string-ids'},
        {'Authorization': f'Token {token}'},
    ]
    
    endpoints_to_try = [
        '/api/v1/users/self',
        '/api/v1/accounts/self',
        '/api/v1/courses'
    ]
    
    for i, headers in enumerate(headers_to_try, 1):
        print(f"\n--- Test {i}: Headers = {headers} ---")
        
        for endpoint in endpoints_to_try:
            full_url = f"{url}{endpoint}"
            print(f"\nTesting: {full_url}")
            
            try:
                response = requests.get(full_url, headers=headers, timeout=10)
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print("✅ SUCCESS! Response:")
                    print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2))
                    return True
                elif response.status_code == 401:
                    print("❌ 401 Unauthorized - Token may be invalid or expired")
                    print(f"Response body: {response.text[:200]}")
                elif response.status_code == 403:
                    print("❌ 403 Forbidden - Token may not have required permissions")
                    print(f"Response body: {response.text[:200]}")
                else:
                    print(f"❌ Status {response.status_code}: {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
    
    # Try different Canvas URLs
    alternative_urls = [
        'https://canvas.usfca.edu',
        'https://usfca.canvas.com',
        'https://usfca-edu.canvas.com'
    ]
    
    print(f"\n{'='*60}")
    print("TRYING ALTERNATIVE CANVAS URLs")
    print(f"{'='*60}")
    
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
    
    for alt_url in alternative_urls:
        print(f"\nTrying URL: {alt_url}")
        try:
            response = requests.get(f"{alt_url}/api/v1/users/self", headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ SUCCESS with alternative URL!")
                data = response.json()
                print(f"User: {data.get('name', 'Unknown')}")
                return alt_url
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed: {e}")
    
    return False

if __name__ == "__main__":
    result = debug_canvas_connection()
    if result and isinstance(result, str):
        print(f"\n🎉 Working Canvas URL found: {result}")
        print("\nUpdate your .env file with:")
        print(f"CANVAS_API_URL={result}")
    elif not result:
        print("\n❌ No working configuration found")
        print("\nPossible issues:")
        print("1. Token may be expired or invalid")
        print("2. Canvas URL may be incorrect")
        print("3. Token may not have required API access permissions")
        print("4. Institution may have restricted API access")