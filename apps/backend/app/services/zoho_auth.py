"""Zoho OAuth token management and refresh utility."""

import requests
import time
from typing import Dict, Optional, List, Any
from ..config.config import settings


class ZohoAuthService:
    """Handle Zoho OAuth token refresh and validation."""
    
    def __init__(self):
        self.client_id = settings.zoho_client_id
        self.client_secret = settings.zoho_client_secret
        self.refresh_token = settings.zoho_refresh_token
        self.access_token = settings.zoho_access_token
        self.token_url = "https://accounts.zoho.com/oauth/v2/token"
        self.api_domain = settings.zoho_api_domain
        
    def refresh_access_token(self) -> Dict[str, str]:
        """Refresh the Zoho access token using refresh token."""
        try:
            print("🔄 Refreshing Zoho access token...")
            
            payload = {
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token'
            }
            
            response = requests.post(self.token_url, data=payload)
            
            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get('access_token')
                
                if new_access_token:
                    print("   ✅ Token refresh successful")
                    
                    # Update the current token in memory
                    self.access_token = new_access_token
                    
                    return {
                        'success': True,
                        'access_token': new_access_token,
                        'expires_in': token_data.get('expires_in', 3600),
                        'token_type': token_data.get('token_type', 'Bearer'),
                        'api_domain': token_data.get('api_domain', self.api_domain),
                        'scope': token_data.get('scope', 'ZohoCRM.modules.ALL')
                    }
                else:
                    print("   ❌ No access token in response")
                    return {'success': False, 'error': 'No access token received'}
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error_description', f'HTTP {response.status_code}')
                print(f"   ❌ Token refresh failed: {error_message}")
                return {'success': False, 'error': error_message}
                
        except Exception as e:
            print(f"   ❌ Token refresh exception: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if needed."""
        # First try current token
        if self.access_token and self.validate_token(self.access_token):
            return self.access_token
        
        # If current token is invalid, refresh it
        refresh_result = self.refresh_access_token()
        if refresh_result.get('success'):
            self.access_token = refresh_result['access_token']
            return self.access_token
        
        return None
    
    def validate_token(self, token: str) -> bool:
        """Validate if a token is still working."""
        try:
            headers = {'Authorization': f'Zoho-oauthtoken {token}'}
            response = requests.get(
                'https://www.zohoapis.com/crm/v2/org', 
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with valid access token."""
        valid_token = self.get_valid_token()
        if valid_token:
            return {
                'Authorization': f'Zoho-oauthtoken {valid_token}',
                'Accept': 'application/json'
            }
        else:
            raise Exception("Unable to get valid Zoho access token")
    
    def test_api_access(self) -> Dict[str, any]:
        """Test API access with current/refreshed token."""
        try:
            headers = self.get_headers()
            
            # Test organization endpoint
            response = requests.get('https://www.zohoapis.com/crm/v2/org', headers=headers)
            
            if response.status_code == 200:
                org_data = response.json()
                org_name = "Unknown"
                if 'org' in org_data and org_data['org']:
                    org_name = org_data['org'][0].get('company_name', 'Unknown')
                
                return {
                    'success': True,
                    'organization': org_name,
                    'access_validated': True
                }
            else:
                return {
                    'success': False,
                    'error': f'API test failed: {response.status_code}',
                    'response': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API test exception: {str(e)}'
            }
    
    def get_survey_data_from_module(self, module_name: str, limit: int = 200) -> Dict[str, Any]:
        """Fetch survey/feedback data from a specific Zoho CRM module."""
        try:
            headers = self.get_headers()
            
            # Survey-related fields to look for (based on dev-kit patterns)
            survey_fields = [
                'Course_Name', 'Program_Name', 'Official_Program_Name', 'Programs',
                'Rating', 'Feedback', 'Comments', 'Review', 'Satisfaction_Score', 'NPS_Score',
                'Email', 'Full_Name', 'Contact_Name', 'Student_ID',
                'Created_Time', 'Modified_Time', 'Owner',
                'Priority', 'Issue_Type', 'Show_Stopper'
            ]
            
            # Build request parameters
            params = {
                'per_page': limit,
                'fields': ','.join(survey_fields)
            }
            
            print(f"📊 Fetching survey data from {module_name}...")
            
            response = requests.get(
                f"{self.api_domain}/crm/v2/{module_name}",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('data', [])
                
                # Filter records for survey/feedback relevance
                survey_records = []
                for record in records:
                    if self._has_survey_data(record):
                        survey_records.append(record)
                
                print(f"   ✅ Found {len(records)} total records, {len(survey_records)} with survey data")
                
                return {
                    'success': True,
                    'module': module_name,
                    'total_records': len(records),
                    'survey_records': len(survey_records),
                    'data': survey_records,
                    'raw_data': records  # Keep raw data for debugging
                }
                
            elif response.status_code == 204:
                print(f"   ℹ️  No records found in {module_name}")
                return {
                    'success': True,
                    'module': module_name,
                    'total_records': 0,
                    'survey_records': 0,
                    'data': []
                }
            else:
                print(f"   ❌ Failed to fetch from {module_name}: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text[:200]}',
                    'module': module_name
                }
                
        except Exception as e:
            print(f"   ❌ Error fetching from {module_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'module': module_name
            }
    
    def _has_survey_data(self, record: Dict[str, Any]) -> bool:
        """Check if a record contains survey/feedback data."""
        survey_indicators = [
            'course', 'program', 'training', 'rating', 'feedback', 
            'comment', 'review', 'satisfaction', 'evaluation'
        ]
        
        for key, value in record.items():
            if key.startswith('$'):  # Skip system fields
                continue
                
            key_lower = key.lower()
            
            # Check if field name indicates survey data
            if any(indicator in key_lower for indicator in survey_indicators):
                # Also check if the field has actual content
                if value and str(value).strip() not in ['', 'None', 'null']:
                    return True
        
        return False
    
    def get_all_survey_data(self) -> Dict[str, Any]:
        """Fetch survey data from all relevant Zoho CRM modules."""
        print("🔄 Fetching all Zoho survey data...")
        
        # Priority modules for course feedback (based on dev-kit patterns)
        priority_modules = [
            'Contacts',      # Students/Participants with program enrollment data
            'Leads',         # Prospective students with program interest
            'Deals',         # Course enrollments with program details
            'Accounts',      # Organizations with training programs
            'Products',      # Courses as products
            'Cases',         # Support/Issues related to courses
            'Notes',         # Feedback notes
            'Events',        # Course sessions
            'Tasks'          # Follow-up tasks
        ]
        
        all_survey_data = {
            'timestamp': time.time(),
            'modules_checked': [],
            'modules_with_data': [],
            'total_survey_records': 0,
            'survey_data': {},
            'errors': []
        }
        
        for module_name in priority_modules:
            try:
                print(f"\n📂 Checking {module_name} module...")
                
                result = self.get_survey_data_from_module(module_name)
                all_survey_data['modules_checked'].append(module_name)
                
                if result.get('success'):
                    if result.get('survey_records', 0) > 0:
                        all_survey_data['modules_with_data'].append(module_name)
                        all_survey_data['survey_data'][module_name] = result
                        all_survey_data['total_survey_records'] += result.get('survey_records', 0)
                        
                        print(f"   ✅ {module_name}: {result.get('survey_records')} survey records")
                    else:
                        print(f"   ℹ️  {module_name}: No survey data found")
                else:
                    all_survey_data['errors'].append({
                        'module': module_name,
                        'error': result.get('error', 'Unknown error')
                    })
                    print(f"   ❌ {module_name}: {result.get('error', 'Unknown error')}")
                
                # Rate limiting - be respectful to Zoho API
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"Exception processing {module_name}: {str(e)}"
                all_survey_data['errors'].append({
                    'module': module_name,
                    'error': error_msg
                })
                print(f"   ❌ {error_msg}")
        
        print(f"\n📊 Survey data collection complete:")
        print(f"   Modules checked: {len(all_survey_data['modules_checked'])}")
        print(f"   Modules with survey data: {len(all_survey_data['modules_with_data'])}")
        print(f"   Total survey records: {all_survey_data['total_survey_records']}")
        print(f"   Errors: {len(all_survey_data['errors'])}")
        
        return all_survey_data