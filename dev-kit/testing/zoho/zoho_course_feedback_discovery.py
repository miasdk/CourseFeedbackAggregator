#!/usr/bin/env python3
"""
Zoho CRM Course Feedback Data Discovery Script
Purpose: Discover course feedback data in Zoho CRM standard and custom modules
Based on Zoho CRM API v8 documentation: https://www.zoho.com/crm/developer/docs/api/v8/

Key Modules to Check (from Zoho docs):
- Leads: Potential students/participants
- Contacts: Enrolled students/participants  
- Accounts: Organizations/Companies
- Deals: Course enrollments/registrations
- Tasks/Events: Course schedules
- Custom Modules: Course-specific feedback modules
- Notes/Attachments: Feedback documents
"""

import os
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Try to import required packages
try:
    import requests
except ImportError:
    print("❌ requests package not found. Installing...")
    os.system("pip3 install --user requests")
    import requests

# Load environment variables directly from file
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

class ZohoCourseDataDiscovery:
    """Discover course feedback data in Zoho CRM using API v2"""
    
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.redirect_uri = 'https://miaelena.vercel.app/'
        self.accounts_url = 'https://accounts.zoho.com'
        self.api_domain = 'https://www.zohoapis.com'  # API domain for CRM operations
        self.access_token = os.getenv('ZOHO_ACCESS_TOKEN')  # Use existing token first
        self.headers = {}
        
        # Standard Zoho CRM modules (from API docs)
        # Reference: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html
        self.standard_modules = [
            'Leads',           # Prospective students
            'Contacts',        # Current/past students
            'Accounts',        # Organizations/Companies
            'Deals',           # Course enrollments
            'Tasks',           # Follow-up tasks
            'Events',          # Course sessions/events
            'Calls',           # Phone feedback
            'Meetings',        # Course meetings
            'Products',        # Courses as products
            'Vendors',         # Training providers
            'Campaigns',       # Course campaigns
            'Cases',           # Support tickets/issues
            'Solutions',       # Course improvements
            'Activities',      # Student activities
            'Notes'            # Feedback notes
        ]
        
        # Fields we need for course feedback (based on our requirements)
        self.required_fields = {
            'course_info': ['Course_Name', 'Course_Code', 'Course_ID', 'Program', 'Module', 'Session'],
            'feedback': ['Rating', 'Feedback', 'Comments', 'Review', 'Satisfaction_Score', 'NPS_Score'],
            'student_info': ['Email', 'Full_Name', 'Company', 'Student_ID', 'Contact_Name'],
            'metadata': ['Created_Time', 'Modified_Time', 'Created_By', 'Owner'],
            'priority': ['Priority', 'Severity', 'Show_Stopper', 'Issue_Type', 'Category']
        }
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using Zoho OAuth v2 or use existing token"""
        
        # First try to use existing access token
        if self.access_token:
            self.headers = {
                'Authorization': f'Zoho-oauthtoken {self.access_token}'
            }
            print("✅ Using existing access token")
            return True
        
        # If no access token, refresh it
        token_url = f"{self.accounts_url}/oauth/v2/token"
        
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.headers = {
                    'Authorization': f'Zoho-oauthtoken {self.access_token}'
                }
                print("✅ Access token refreshed successfully")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error refreshing token: {str(e)}")
            return False
    
    def get_all_modules(self) -> List[Dict]:
        """Get all modules including custom modules
        Reference: https://www.zoho.com/crm/developer/docs/api/v2/modules-api.html"""
        
        print("\n📦 Getting all Zoho CRM modules...")
        
        try:
            # Use v2 API endpoint for modules (most stable)
            response = requests.get(
                f"{self.api_domain}/crm/v2/settings/modules",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                modules = data.get('modules', [])
                
                print(f"✓ Found {len(modules)} total modules")
                
                # Categorize modules
                standard = []
                custom = []
                
                for module in modules:
                    module_info = {
                        'api_name': module.get('api_name'),
                        'module_name': module.get('module_name'),
                        'plural_label': module.get('plural_label'),
                        'singular_label': module.get('singular_label'),
                        'custom_module': module.get('generated_type') == 'custom',
                        'api_supported': module.get('api_supported', False),
                        'quick_create': module.get('quick_create', False),
                        'feeds': module.get('feeds', False),
                        'scoring': module.get('scoring_supported', False),
                        'webform': module.get('webform_supported', False)
                    }
                    
                    if module_info['custom_module']:
                        custom.append(module_info)
                        print(f"   🔧 Custom: {module_info['plural_label']} ({module_info['api_name']})")
                    else:
                        standard.append(module_info)
                
                return {
                    'standard_modules': standard,
                    'custom_modules': custom,
                    'all_modules': modules
                }
            else:
                print(f"❌ Failed to get modules: {response.status_code}")
                print(response.text)
                return {}
                
        except Exception as e:
            print(f"❌ Error getting modules: {str(e)}")
            return {}
    
    def get_module_metadata(self, module_name: str) -> Dict:
        """Get detailed metadata for a module including all fields
        Reference: https://www.zoho.com/crm/developer/docs/api/v2/module-meta.html"""
        
        print(f"\n🔍 Getting metadata for module: {module_name}")
        
        try:
            # Use v2 API for module metadata
            response = requests.get(
                f"{self.api_domain}/crm/v2/settings/modules/{module_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                module_data = data.get('modules', [{}])[0]
                
                # Extract fields
                fields = module_data.get('fields', [])
                
                # Categorize fields based on our requirements
                categorized_fields = {
                    'course_fields': [],
                    'feedback_fields': [],
                    'student_fields': [],
                    'priority_fields': [],
                    'date_fields': [],
                    'all_custom_fields': []
                }
                
                for field in fields:
                    field_info = {
                        'api_name': field.get('api_name'),
                        'field_label': field.get('field_label'),
                        'data_type': field.get('data_type'),
                        'length': field.get('length'),
                        'custom_field': field.get('custom_field', False),
                        'mandatory': field.get('system_mandatory', False),
                        'pick_list_values': field.get('pick_list_values', [])
                    }
                    
                    api_name_lower = field_info['api_name'].lower()
                    label_lower = field_info['field_label'].lower()
                    
                    # Custom fields
                    if field_info['custom_field']:
                        categorized_fields['all_custom_fields'].append(field_info)
                    
                    # Course-related fields
                    if any(term in api_name_lower or term in label_lower 
                           for term in ['course', 'program', 'module', 'session', 'training', 'workshop']):
                        categorized_fields['course_fields'].append(field_info)
                        print(f"   📚 Course field: {field_info['field_label']} ({field_info['api_name']})")
                    
                    # Feedback fields
                    elif any(term in api_name_lower or term in label_lower 
                             for term in ['rating', 'feedback', 'comment', 'review', 'satisfaction', 
                                        'nps', 'score', 'evaluation', 'assessment']):
                        categorized_fields['feedback_fields'].append(field_info)
                        print(f"   💬 Feedback field: {field_info['field_label']} ({field_info['api_name']})")
                    
                    # Student/Contact fields
                    elif any(term in api_name_lower or term in label_lower 
                             for term in ['email', 'student', 'participant', 'learner', 'attendee']):
                        categorized_fields['student_fields'].append(field_info)
                        print(f"   👤 Student field: {field_info['field_label']} ({field_info['api_name']})")
                    
                    # Priority/Issue fields
                    elif any(term in api_name_lower or term in label_lower 
                             for term in ['priority', 'severity', 'issue', 'problem', 'blocker', 'critical']):
                        categorized_fields['priority_fields'].append(field_info)
                        print(f"   ⚠️  Priority field: {field_info['field_label']} ({field_info['api_name']})")
                    
                    # Date fields
                    elif field_info['data_type'] in ['datetime', 'date']:
                        categorized_fields['date_fields'].append(field_info)
                
                return {
                    'module_name': module_name,
                    'total_fields': len(fields),
                    'custom_field_count': len(categorized_fields['all_custom_fields']),
                    'categorized_fields': categorized_fields,
                    'has_feedback_data': bool(categorized_fields['feedback_fields'] or 
                                            categorized_fields['course_fields'])
                }
            else:
                print(f"   ⚠️  Could not get metadata: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Error getting metadata: {str(e)}")
            return {}
    
    def get_records_with_criteria(self, module_name: str, search_criteria: Dict = None) -> Dict:
        """Get records from a module with optional search criteria
        Reference: https://www.zoho.com/crm/developer/docs/api/v2/get-records.html"""
        
        print(f"\n📊 Getting records from: {module_name}")
        
        try:
            # Build parameters
            params = {
                'per_page': 10
            }
            
            # Add search criteria if provided
            if search_criteria:
                if 'criteria' in search_criteria:
                    params['criteria'] = search_criteria['criteria']
                if 'fields' in search_criteria:
                    params['fields'] = search_criteria['fields']
            
            # Use v2 API
            response = requests.get(
                f"{self.api_domain}/crm/v2/{module_name}",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('data', [])
                
                if records:
                    print(f"   ✓ Found {len(records)} records")
                    
                    # Analyze first record for course feedback patterns
                    analysis = self.analyze_record_for_feedback(records[0])
                    
                    return {
                        'module': module_name,
                        'record_count': len(records),
                        'has_feedback_data': analysis['has_feedback_data'],
                        'feedback_fields_found': analysis['feedback_fields'],
                        'sample_record': records[0] if records else {},
                        'records': records
                    }
                else:
                    print(f"   ℹ️  No records found")
                    return {
                        'module': module_name,
                        'record_count': 0,
                        'has_feedback_data': False
                    }
            elif response.status_code == 204:
                print(f"   ℹ️  No records in module")
                return {
                    'module': module_name,
                    'record_count': 0,
                    'has_feedback_data': False
                }
            else:
                print(f"   ⚠️  Could not get records: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Error getting records: {str(e)}")
            return {}
    
    def analyze_record_for_feedback(self, record: Dict) -> Dict:
        """Analyze a record to identify feedback-related fields"""
        
        feedback_fields = []
        course_fields = []
        student_fields = []
        
        for key, value in record.items():
            key_lower = key.lower()
            
            # Skip system fields
            if key.startswith('$'):
                continue
            
            # Check for feedback fields
            if any(term in key_lower for term in 
                   ['rating', 'feedback', 'comment', 'review', 'satisfaction', 'score', 'evaluation']):
                feedback_fields.append({
                    'field': key,
                    'value': value,
                    'type': type(value).__name__
                })
            
            # Check for course fields
            elif any(term in key_lower for term in 
                     ['course', 'program', 'training', 'session', 'module', 'workshop']):
                course_fields.append({
                    'field': key,
                    'value': value,
                    'type': type(value).__name__
                })
            
            # Check for student fields
            elif any(term in key_lower for term in 
                     ['email', 'student', 'participant', 'name', 'contact']):
                student_fields.append({
                    'field': key,
                    'value': value,
                    'type': type(value).__name__
                })
        
        return {
            'has_feedback_data': bool(feedback_fields or course_fields),
            'feedback_fields': feedback_fields,
            'course_fields': course_fields,
            'student_fields': student_fields
        }
    
    def search_module_for_keywords(self, module_name: str, keywords: List[str]) -> Dict:
        """Search a module for specific keywords
        Reference: https://www.zoho.com/crm/developer/docs/api/v2/search-records.html"""
        
        print(f"\n🔎 Searching {module_name} for course feedback keywords...")
        
        results = {}
        
        for keyword in keywords:
            try:
                # Use search API with word parameter
                response = requests.get(
                    f"{self.api_domain}/crm/v2/{module_name}/search",
                    headers=self.headers,
                    params={
                        'word': keyword,
                        'per_page': 5
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('data', [])
                    if records:
                        print(f"   ✓ Found {len(records)} records containing '{keyword}'")
                        results[keyword] = {
                            'count': len(records),
                            'sample': records[0] if records else None
                        }
                elif response.status_code != 204:  # 204 means no content/no results
                    print(f"   ⚠️  Search issue for '{keyword}': {response.status_code}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"   ⚠️  Error searching for '{keyword}': {str(e)}")
        
        return results
    
    def check_custom_modules(self) -> List[Dict]:
        """Check for custom modules that might contain course feedback"""
        
        print("\n🔧 Checking for custom course feedback modules...")
        
        modules_data = self.get_all_modules()
        custom_modules = modules_data.get('custom_modules', [])
        
        feedback_modules = []
        
        for module in custom_modules:
            module_name = module['api_name']
            
            # Get metadata
            metadata = self.get_module_metadata(module_name)
            
            if metadata.get('has_feedback_data'):
                print(f"   ✅ Found feedback module: {module['plural_label']}")
                feedback_modules.append({
                    'module_name': module_name,
                    'display_name': module['plural_label'],
                    'metadata': metadata
                })
            
            time.sleep(0.5)  # Rate limiting
        
        return feedback_modules
    
    def run_comprehensive_discovery(self) -> Dict:
        """Run comprehensive discovery of course feedback data"""
        
        print("\n" + "="*60)
        print("🚀 ZOHO CRM COURSE FEEDBACK DISCOVERY")
        print("="*60)
        
        discovery_report = {
            'timestamp': datetime.now().isoformat(),
            'api_version': 'v2',
            'modules_analyzed': [],
            'feedback_modules': [],
            'recommended_integration': {},
            'field_mappings': {},
            'sample_data': {}
        }
        
        # 1. Authenticate
        if not self.refresh_access_token():
            discovery_report['error'] = "Authentication failed"
            return discovery_report
        
        # 2. Get all modules
        print("\n📦 STEP 1: Module Discovery")
        print("-" * 40)
        modules_data = self.get_all_modules()
        
        if not modules_data:
            discovery_report['error'] = "Could not retrieve modules"
            return discovery_report
        
        # 3. Priority modules to check (based on typical CRM usage for training/courses)
        priority_modules = [
            'Contacts',      # Students/Participants
            'Leads',         # Prospective students
            'Accounts',      # Companies/Organizations
            'Deals',         # Course enrollments
            'Products',      # Courses as products
            'Cases',         # Support/Issues
            'Tasks',         # Follow-ups
            'Events',        # Course sessions
            'Notes'          # Feedback notes
        ]
        
        # 4. Check standard modules first
        print("\n📊 STEP 2: Analyzing Standard Modules")
        print("-" * 40)
        
        for module_name in priority_modules:
            print(f"\nChecking {module_name}...")
            
            # Get metadata
            metadata = self.get_module_metadata(module_name)
            
            if metadata:
                discovery_report['modules_analyzed'].append(module_name)
                
                # Get sample records
                records = self.get_records_with_criteria(module_name)
                
                if records.get('has_feedback_data'):
                    discovery_report['feedback_modules'].append({
                        'module': module_name,
                        'type': 'standard',
                        'feedback_fields': metadata.get('categorized_fields', {}).get('feedback_fields', []),
                        'course_fields': metadata.get('categorized_fields', {}).get('course_fields', []),
                        'record_count': records.get('record_count', 0)
                    })
                    
                    # Store sample data
                    if records.get('sample_record'):
                        discovery_report['sample_data'][module_name] = records.get('sample_record')
                
                # Search for keywords
                search_results = self.search_module_for_keywords(
                    module_name, 
                    ['course', 'training', 'feedback', 'evaluation']
                )
                
                if search_results:
                    discovery_report['modules_analyzed'].append(f"{module_name}_search")
            
            time.sleep(1)  # Rate limiting
        
        # 5. Check custom modules
        print("\n🔧 STEP 3: Analyzing Custom Modules")
        print("-" * 40)
        
        custom_feedback_modules = self.check_custom_modules()
        
        for custom_module in custom_feedback_modules:
            discovery_report['feedback_modules'].append({
                'module': custom_module['module_name'],
                'type': 'custom',
                'display_name': custom_module['display_name'],
                'metadata': custom_module['metadata']
            })
        
        # 6. Generate recommendations
        print("\n📋 STEP 4: Generating Integration Recommendations")
        print("-" * 40)
        
        if discovery_report['feedback_modules']:
            # Find the best module for course feedback
            best_module = None
            for module in discovery_report['feedback_modules']:
                if module['type'] == 'custom' and 'feedback' in module.get('display_name', '').lower():
                    best_module = module
                    break
            
            if not best_module and discovery_report['feedback_modules']:
                best_module = discovery_report['feedback_modules'][0]
            
            discovery_report['recommended_integration'] = {
                'primary_module': best_module['module'] if best_module else None,
                'secondary_modules': [m['module'] for m in discovery_report['feedback_modules'] 
                                    if m != best_module][:2],
                'integration_approach': 'custom_module' if best_module and best_module['type'] == 'custom' 
                                       else 'standard_module_extension'
            }
            
            print(f"\n✅ Recommended Primary Module: {best_module['module'] if best_module else 'None'}")
        
        return discovery_report
    
    def save_results(self, report: Dict):
        """Save discovery results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full report
        report_filename = f"zoho_discovery_report_{timestamp}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Full report saved to: {report_filename}")
        
        # Create field mapping template
        if report.get('feedback_modules'):
            mapping = {
                'zoho_to_unified_schema': {},
                'modules': {}
            }
            
            for module_data in report['feedback_modules']:
                module_name = module_data['module']
                mapping['modules'][module_name] = {
                    'type': module_data['type'],
                    'unified_mappings': {
                        'course_id': None,
                        'course_name': None,
                        'student_email': None,
                        'student_name': None,
                        'rating': None,
                        'feedback_text': None,
                        'created_date': None,
                        'priority': None,
                        'issue_category': None
                    },
                    'available_fields': module_data.get('feedback_fields', []) + 
                                      module_data.get('course_fields', [])
                }
            
            mapping_filename = f"zoho_schema_mapping_{timestamp}.json"
            with open(mapping_filename, 'w') as f:
                json.dump(mapping, f, indent=2)
            print(f"📋 Schema mapping template saved to: {mapping_filename}")

def main():
    """Run the Zoho CRM course feedback discovery"""
    
    discovery = ZohoCourseDataDiscovery()
    
    # Run comprehensive discovery
    report = discovery.run_comprehensive_discovery()
    
    # Save results
    discovery.save_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DISCOVERY SUMMARY")
    print("="*60)
    
    if report.get('error'):
        print(f"❌ Discovery failed: {report['error']}")
    else:
        print(f"✅ Modules analyzed: {len(report.get('modules_analyzed', []))}")
        print(f"✅ Feedback modules found: {len(report.get('feedback_modules', []))}")
        
        if report.get('recommended_integration'):
            print(f"\n🎯 RECOMMENDED INTEGRATION:")
            print(f"   Primary Module: {report['recommended_integration'].get('primary_module')}")
            print(f"   Approach: {report['recommended_integration'].get('integration_approach')}")
        
        if report.get('feedback_modules'):
            print(f"\n📦 MODULES WITH FEEDBACK DATA:")
            for module in report['feedback_modules']:
                print(f"   • {module['module']} ({module['type']})")
                if module.get('record_count'):
                    print(f"     Records: {module['record_count']}")

if __name__ == "__main__":
    main()