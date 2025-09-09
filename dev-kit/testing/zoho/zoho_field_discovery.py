#!/usr/bin/env python3
"""
Zoho Field Discovery - Get actual field names from records
"""

import os
import json
import sys

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip3 install --user requests")
    import requests

# Load environment variables
def load_env_file(filepath):
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

env_path = os.path.join(os.path.dirname(__file__), '../../../.env')
env_vars = load_env_file(env_path)

access_token = os.getenv('ZOHO_ACCESS_TOKEN')
headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}

print("="*60)
print("🔍 ZOHO CRM FIELD DISCOVERY")
print("="*60)

modules = ['Contacts', 'Deals', 'Accounts', 'Leads']

all_fields = {}

for module in modules:
    print(f"\n📊 Discovering fields in {module}...")
    
    try:
        # Get a few records to see all field names
        response = requests.get(
            f"https://www.zohoapis.com/crm/v2/{module}",
            headers=headers,
            params={'per_page': 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('data', [])
            
            if records:
                # Get all unique field names from first record
                sample_record = records[0]
                field_names = list(sample_record.keys())
                
                # Categorize fields
                feedback_fields = []
                course_fields = []
                student_fields = []
                date_fields = []
                other_fields = []
                
                for field in field_names:
                    if field.startswith('$'):
                        continue
                        
                    field_lower = field.lower()
                    sample_value = sample_record.get(field)
                    
                    # Check field type
                    if any(term in field_lower for term in 
                           ['feedback', 'review', 'rating', 'score', 'comment', 'satisfaction', 'nps']):
                        feedback_fields.append((field, type(sample_value).__name__, str(sample_value)[:50] if sample_value else None))
                    elif any(term in field_lower for term in 
                             ['course', 'program', 'training', 'workshop', 'session', 'class']):
                        course_fields.append((field, type(sample_value).__name__, str(sample_value)[:50] if sample_value else None))
                    elif any(term in field_lower for term in 
                             ['email', 'name', 'student', 'participant', 'contact']):
                        student_fields.append((field, type(sample_value).__name__, str(sample_value)[:50] if sample_value else None))
                    elif any(term in field_lower for term in 
                             ['date', 'time', 'created', 'modified']):
                        date_fields.append((field, type(sample_value).__name__, str(sample_value)[:20] if sample_value else None))
                    else:
                        # Only show fields with actual data
                        if sample_value:
                            other_fields.append((field, type(sample_value).__name__, str(sample_value)[:30] if sample_value else None))
                
                all_fields[module] = {
                    'total_fields': len(field_names),
                    'feedback_fields': feedback_fields,
                    'course_fields': course_fields,
                    'student_fields': student_fields,
                    'date_fields': date_fields,
                    'other_fields': other_fields[:10]  # Limit other fields
                }
                
                print(f"   ✅ Found {len(field_names)} total fields")
                
                if feedback_fields:
                    print(f"   💬 Feedback fields ({len(feedback_fields)}):")
                    for field, type_name, sample in feedback_fields:
                        print(f"      • {field} ({type_name}): {sample}")
                
                if course_fields:
                    print(f"   📚 Course fields ({len(course_fields)}):")
                    for field, type_name, sample in course_fields:
                        print(f"      • {field} ({type_name}): {sample}")
                
                if student_fields:
                    print(f"   👤 Student fields ({len(student_fields)}):")
                    for field, type_name, sample in student_fields[:5]:  # Limit to 5
                        print(f"      • {field} ({type_name}): {sample}")
            else:
                print(f"   ⚠️  No records found")
        else:
            print(f"   ❌ Error {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

# Save results
with open('zoho_field_discovery.json', 'w') as f:
    json.dump(all_fields, f, indent=2, default=str)

print(f"\n💾 Field discovery saved to: zoho_field_discovery.json")

# Generate summary
print(f"\n📋 SUMMARY:")
for module, fields in all_fields.items():
    feedback_count = len(fields.get('feedback_fields', []))
    course_count = len(fields.get('course_fields', []))
    
    if feedback_count > 0 or course_count > 0:
        print(f"   {module}: {feedback_count} feedback fields, {course_count} course fields")