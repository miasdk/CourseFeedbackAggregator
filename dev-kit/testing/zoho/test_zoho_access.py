#!/usr/bin/env python3
"""
Simple test to verify Zoho CRM API access and discover what we can access
"""

import os
import sys
import json

# Try to import requests
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip3 install --user requests")
    import requests

# Load environment variables
def load_env_file(filepath):
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        print(f"❌ .env file not found at {filepath}")
        return {}

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
env_vars = load_env_file(env_path)

# Get credentials
access_token = os.getenv('ZOHO_ACCESS_TOKEN')
refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
client_id = os.getenv('ZOHO_CLIENT_ID')
client_secret = os.getenv('ZOHO_CLIENT_SECRET')

print("="*60)
print("ZOHO CRM API ACCESS TEST")
print("="*60)
print()

# Set up headers
headers = {
    'Authorization': f'Zoho-oauthtoken {access_token}'
}

# Test different endpoints to see what we can access
test_endpoints = [
    ('Organization Info', 'https://www.zohoapis.com/crm/v2/org'),
    ('Users', 'https://www.zohoapis.com/crm/v2/users'),
    ('Modules Settings', 'https://www.zohoapis.com/crm/v2/settings/modules'),
    ('Leads Module', 'https://www.zohoapis.com/crm/v2/Leads'),
    ('Contacts Module', 'https://www.zohoapis.com/crm/v2/Contacts'),
    ('Accounts Module', 'https://www.zohoapis.com/crm/v2/Accounts'),
    ('Deals Module', 'https://www.zohoapis.com/crm/v2/Deals'),
    ('Products Module', 'https://www.zohoapis.com/crm/v2/Products'),
    ('Tasks Module', 'https://www.zohoapis.com/crm/v2/Tasks'),
    ('Events Module', 'https://www.zohoapis.com/crm/v2/Events'),
    ('Notes Module', 'https://www.zohoapis.com/crm/v2/Notes'),
    ('Custom Module', 'https://www.zohoapis.com/crm/v2/Custom')
]

print("Testing API endpoints:")
print("-" * 40)

accessible_endpoints = []
data_found = {}

for name, endpoint in test_endpoints:
    try:
        response = requests.get(endpoint, headers=headers, params={'per_page': 1})
        
        if response.status_code == 200:
            print(f"✅ {name}: SUCCESS")
            accessible_endpoints.append(name)
            
            # Try to get sample data
            data = response.json()
            if 'data' in data and data['data']:
                print(f"   → Found {len(data['data'])} record(s)")
                # Store first record for analysis
                data_found[name] = data['data'][0] if data['data'] else {}
            elif 'modules' in data:
                print(f"   → Found {len(data['modules'])} module(s)")
                # List first few modules
                for module in data['modules'][:3]:
                    print(f"      • {module.get('plural_label', 'Unknown')} ({module.get('api_name', 'Unknown')})")
            elif 'org' in data:
                print(f"   → Organization: {data['org'][0].get('company_name', 'Unknown')}")
            elif 'users' in data:
                print(f"   → Found {len(data['users'])} user(s)")
                
        elif response.status_code == 204:
            print(f"⚠️  {name}: NO DATA (empty module)")
            accessible_endpoints.append(f"{name} (empty)")
            
        elif response.status_code == 401:
            error_data = response.json()
            error_code = error_data.get('code', 'UNKNOWN')
            if error_code == 'OAUTH_SCOPE_MISMATCH':
                print(f"❌ {name}: SCOPE MISMATCH")
            elif error_code == 'INVALID_TOKEN':
                print(f"❌ {name}: INVALID TOKEN")
            else:
                print(f"❌ {name}: UNAUTHORIZED - {error_code}")
                
        elif response.status_code == 404:
            print(f"⚠️  {name}: NOT FOUND (module might not exist)")
            
        else:
            print(f"❌ {name}: ERROR {response.status_code}")
            
    except Exception as e:
        print(f"❌ {name}: EXCEPTION - {str(e)}")

print()
print("="*60)
print("SUMMARY")
print("="*60)
print(f"✅ Accessible endpoints: {len(accessible_endpoints)}")
for endpoint in accessible_endpoints:
    print(f"   • {endpoint}")

# If we found data, analyze it for course feedback patterns
if data_found:
    print()
    print("📊 DATA ANALYSIS")
    print("-" * 40)
    
    for module_name, record in data_found.items():
        feedback_fields = []
        course_fields = []
        
        for key in record.keys():
            key_lower = key.lower()
            
            # Skip system fields
            if key.startswith('$'):
                continue
                
            # Check for feedback-related fields
            if any(term in key_lower for term in ['rating', 'feedback', 'comment', 'review', 'satisfaction', 'score']):
                feedback_fields.append(key)
            
            # Check for course-related fields
            elif any(term in key_lower for term in ['course', 'program', 'training', 'session', 'workshop']):
                course_fields.append(key)
        
        if feedback_fields or course_fields:
            print(f"\n{module_name}:")
            if feedback_fields:
                print(f"  💬 Feedback fields: {', '.join(feedback_fields)}")
            if course_fields:
                print(f"  📚 Course fields: {', '.join(course_fields)}")

# Save results
results = {
    'test_timestamp': os.popen('date').read().strip(),
    'accessible_endpoints': accessible_endpoints,
    'data_samples': data_found,
    'access_token_valid': len(accessible_endpoints) > 0
}

with open('zoho_access_test_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
    
print()
print(f"💾 Results saved to: zoho_access_test_results.json")