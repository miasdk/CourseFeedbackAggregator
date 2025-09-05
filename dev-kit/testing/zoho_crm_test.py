#!/usr/bin/env python3
"""
Zoho CRM API v8 Comprehensive Testing Script
Complete OAuth flow testing and data discovery for course feedback aggregation
"""
import os
import json
import urllib.parse
import urllib.request
import urllib.error
import time
from pathlib import Path
from datetime import datetime

# Zoho API v8 Configuration
ZOHO_API_BASE = "https://www.zohoapis.com/crm/v8"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/auth"
ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

# OAuth Scopes for different access levels
SCOPES = {
    "minimal": "ZohoCRM.modules.READ,ZohoCRM.settings.READ",
    "standard": "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL",
    "read_only": "ZohoCRM.modules.READ,ZohoCRM.settings.READ,ZohoCRM.users.READ",
    "course_feedback": "ZohoCRM.modules.custom.READ,ZohoCRM.modules.leads.READ,ZohoCRM.modules.contacts.READ,ZohoCRM.settings.READ"
}

# Priority modules for course feedback discovery
PRIORITY_MODULES = ["Custom", "Leads", "Contacts", "Campaigns", "Cases"]
STANDARD_MODULES = ["Accounts", "Deals", "Tasks", "Events", "Calls"]

def load_env():
    """Load .env file from current directory or parent directories"""
    # Try current directory first
    env_path = Path.cwd() / '.env'
    
    # If not found, try parent directories
    if not env_path.exists():
        current_path = Path(__file__).resolve().parent
        for _ in range(3):  # Check up to 3 parent levels
            env_path = current_path / '.env'
            if env_path.exists():
                break
            current_path = current_path.parent
    
    if not env_path.exists():
        print(f"Warning: .env file not found. Searched in current directory and parent paths.")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('"').strip("'")
        
        print(f"Environment loaded from: {env_path}")
        return True
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return False

def validate_token_format(token):
    """Basic validation for token format"""
    if not token:
        return False
    return len(token) > 30 and ('1000.' in token or len(token) > 50)

def make_api_request(endpoint, access_token, method="GET", data=None, max_retries=2):
    """Make authenticated API request with retry logic and rate limiting"""
    # Rate limiting - Zoho allows 100 calls per minute
    time.sleep(0.6)  # 1 call per 600ms = ~100 calls per minute
    
    url = f"{ZOHO_API_BASE}/{endpoint}" if not endpoint.startswith("http") else endpoint
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    for attempt in range(max_retries + 1):
        try:
            request_data = None
            if data:
                request_data = json.dumps(data).encode('utf-8')
            
            request = urllib.request.Request(url, data=request_data, headers=headers)
            request.get_method = lambda: method
            
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                
                # Handle rate limiting
                if e.code == 429:
                    if attempt < max_retries:
                        print(f"Rate limited, waiting 60 seconds... (attempt {attempt + 1})")
                        time.sleep(60)
                        continue
                
                return {"error": True, "status_code": e.code, "details": error_json}
            except:
                return {"error": True, "status_code": e.code, "message": error_body}
        
        except Exception as e:
            if attempt < max_retries:
                print(f"Request failed, retrying... (attempt {attempt + 1})")
                time.sleep(2)
                continue
            return {"error": True, "message": str(e)}
    
    return {"error": True, "message": "Max retries exceeded"}

def test_organization(access_token):
    """Test organization endpoint"""
    print("\n" + "="*60)
    print("Testing Organization Access")
    print("="*60)
    
    result = make_api_request("org", access_token)
    
    if "error" in result:
        print(f"Organization test failed: {result}")
        return False
    
    print("Organization Details Retrieved:")
    if "org" in result and isinstance(result["org"], list) and result["org"]:
        org = result["org"][0]
        print(f"  Company Name: {org.get('company_name', 'N/A')}")
        print(f"  Country: {org.get('country', 'N/A')}")
        print(f"  Time Zone: {org.get('time_zone', 'N/A')}")
        print(f"  Currency: {org.get('currency_symbol', '')} ({org.get('currency_name', 'N/A')})")
        
        license_info = org.get('license_details', {})
        print(f"  License Type: {license_info.get('paid_type', 'N/A')}")
        
    print("Organization test: SUCCESS")
    return True

def discover_modules(access_token):
    """Discover all available CRM modules"""
    print("\n" + "="*60)
    print("Discovering CRM Modules")
    print("="*60)
    
    result = make_api_request("settings/modules", access_token)
    
    if "error" in result:
        print(f"Module discovery failed: {result}")
        return []
    
    available_modules = []
    custom_modules = []
    
    if "modules" in result:
        print(f"Found {len(result['modules'])} total modules:")
        
        for module in result['modules']:
            api_name = module.get('api_name', 'Unknown')
            module_name = module.get('module_name', '')
            generated_type = module.get('generated_type', 'default')
            editable = "Yes" if module.get('editable', False) else "No"
            
            available_modules.append(api_name)
            
            # Track custom modules separately
            if generated_type == 'custom':
                custom_modules.append(api_name)
                print(f"  CUSTOM: {api_name:<20} ({module_name}) [Editable: {editable}]")
            else:
                print(f"  {api_name:<20} ({module_name}) [Editable: {editable}]")
        
        if custom_modules:
            print(f"\nCustom Modules Found: {len(custom_modules)}")
            for custom in custom_modules:
                print(f"  - {custom} (High priority for course feedback)")
        
        print(f"\nModule discovery: SUCCESS ({len(available_modules)} modules)")
    
    return available_modules, custom_modules

def analyze_module_fields(access_token, module_name):
    """Analyze fields in a module to find course-related data"""
    print(f"\n" + "-"*40)
    print(f"Analyzing Fields in {module_name}")
    print("-"*40)
    
    result = make_api_request(f"settings/fields?module={module_name}", access_token)
    
    if "error" in result:
        print(f"Field analysis failed for {module_name}: {result}")
        return []
    
    course_related_fields = []
    all_fields = []
    
    if "fields" in result:
        fields = result["fields"]
        
        # Keywords to identify course/feedback related fields
        course_keywords = [
            'course', 'feedback', 'rating', 'comment', 'review', 'survey',
            'student', 'education', 'module', 'lesson', 'score', 'evaluation'
        ]
        
        print(f"Found {len(fields)} fields in {module_name}:")
        
        for field in fields:
            api_name = field.get('api_name', '')
            field_label = field.get('field_label', '')
            data_type = field.get('data_type', '')
            
            all_fields.append({
                'api_name': api_name,
                'label': field_label,
                'type': data_type
            })
            
            # Check if field might contain course data
            field_text = f"{api_name} {field_label}".lower()
            if any(keyword in field_text for keyword in course_keywords):
                course_related_fields.append({
                    'api_name': api_name,
                    'label': field_label,
                    'type': data_type
                })
                print(f"  COURSE-RELATED: {api_name} ({field_label}) - {data_type}")
            else:
                print(f"  {api_name} ({field_label}) - {data_type}")
        
        if course_related_fields:
            print(f"\nCourse-related fields found: {len(course_related_fields)}")
        else:
            print(f"\nNo obviously course-related fields found in {module_name}")
    
    return course_related_fields

def test_module_data(access_token, module_name, limit=3):
    """Test data retrieval from a specific module"""
    print(f"\n" + "-"*40)
    print(f"Testing Data from {module_name}")
    print("-"*40)
    
    params = {
        "per_page": limit,
        "page": 1,
        "sort_by": "Modified_Time",
        "sort_order": "desc"
    }
    
    query_string = urllib.parse.urlencode(params)
    endpoint = f"{module_name}?{query_string}"
    
    result = make_api_request(endpoint, access_token)
    
    if "error" in result:
        print(f"Data test failed for {module_name}: {result.get('details', result.get('message', 'Unknown error'))}")
        return False, []
    
    records = []
    if "data" in result:
        records = result["data"]
        print(f"Retrieved {len(records)} records from {module_name}:")
        
        for i, record in enumerate(records, 1):
            print(f"\n  Record {i} (ID: {record.get('id', 'N/A')}):")
            
            # Show key fields
            key_fields = ['Last_Name', 'First_Name', 'Company', 'Email', 'Subject', 'Course_Name', 'Rating', 'Comments']
            field_count = 0
            
            for field in key_fields:
                if field in record and record[field] and field_count < 5:
                    print(f"    {field}: {record[field]}")
                    field_count += 1
            
            # Show any other non-system fields
            for key, value in record.items():
                if (not key.startswith('$') and 
                    key not in key_fields and 
                    value and 
                    field_count < 8):
                    print(f"    {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    field_count += 1
            
            if len(record) > field_count:
                print(f"    ... and {len(record) - field_count} more fields")
    
    # Show pagination info
    if "info" in result:
        info = result["info"]
        print(f"\n  Pagination Info:")
        print(f"    Total Records: {info.get('count', 0)}")
        print(f"    Current Page: {info.get('page', 1)}")
        print(f"    Records Per Page: {info.get('per_page', 0)}")
        print(f"    More Records Available: {'Yes' if info.get('more_records', False) else 'No'}")
    
    return True, records

def test_coql_search(access_token):
    """Test COQL for finding course-related data"""
    print(f"\n" + "-"*40)
    print("Testing COQL for Course Data")
    print("-"*40)
    
    # Test queries for course-related data
    test_queries = [
        "SELECT Last_Name, Company FROM Leads WHERE Last_Name LIKE '%Course%' LIMIT 5",
        "SELECT Last_Name, First_Name FROM Contacts WHERE Company LIKE '%Education%' LIMIT 5",
        "SELECT id, Subject FROM Cases WHERE Subject LIKE '%course%' OR Subject LIKE '%feedback%' LIMIT 5"
    ]
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        
        data = {"select_query": query}
        result = make_api_request("coql", access_token, method="POST", data=data)
        
        if "error" in result:
            print(f"  Query failed: {result.get('details', result.get('message', 'Unknown error'))}")
            continue
        
        if "data" in result and result["data"]:
            print(f"  Found {len(result['data'])} matching records")
            for i, record in enumerate(result["data"][:2], 1):  # Show first 2
                print(f"    Record {i}: {record}")
        else:
            print("  No matching records found")
    
    return True

def save_test_results(results):
    """Save test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zoho_crm_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nTest results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"Failed to save results: {e}")
        return None

def generate_oauth_instructions(client_id, client_secret):
    """Generate complete OAuth setup instructions"""
    print("\n" + "="*60)
    print("OAuth Setup Required")
    print("="*60)
    
    print("\nAvailable Scope Options:")
    for key, value in SCOPES.items():
        print(f"  {key}: {value}")
    
    print("\nStep 1: Choose Authorization URL")
    print("-" * 40)
    
    # Generate URLs for different scopes
    for scope_name in ["minimal", "course_feedback"]:
        scope = SCOPES[scope_name]
        params = {
            "scope": scope,
            "client_id": client_id,
            "response_type": "code",
            "access_type": "offline",
            "redirect_uri": "http://localhost:8000/auth/callback"
        }
        
        auth_url = f"{ZOHO_AUTH_URL}?{urllib.parse.urlencode(params)}"
        print(f"\nFor {scope_name.upper()} access:")
        print(f"{auth_url}")
    
    print(f"\nStep 2: Complete Authorization")
    print("-" * 40)
    print("1. Visit one of the URLs above in your browser")
    print("2. Log in to Zoho and authorize the application") 
    print("3. You'll be redirected to: http://localhost:8000/auth/callback?code=YOUR_CODE")
    print("4. Copy the 'code' parameter from the redirect URL")
    
    print(f"\nStep 3: Exchange Code for Tokens")
    print("-" * 40)
    print("Run this curl command with your authorization code:")
    
    curl_cmd = f'''curl -X POST "{ZOHO_TOKEN_URL}" \\
  -d "grant_type=authorization_code" \\
  -d "client_id={client_id}" \\
  -d "client_secret={client_secret}" \\
  -d "redirect_uri=http://localhost:8000/auth/callback" \\
  -d "code=YOUR_AUTHORIZATION_CODE_HERE"'''
    
    print(f"\n{curl_cmd}")
    
    print(f"\nStep 4: Save Tokens")
    print("-" * 40)
    print("Add the returned tokens to your .env file:")
    print("ZOHO_ACCESS_TOKEN=your_access_token_here")
    print("ZOHO_REFRESH_TOKEN=your_refresh_token_here")
    
    print(f"\nStep 5: Run Test Again")
    print("-" * 40)
    print("python zoho_crm_test.py")

def main():
    """Main test execution function"""
    print("Zoho CRM API v8 Comprehensive Testing")
    print("="*60)
    
    # Load environment
    if not load_env():
        print("Warning: Could not load .env file. Using environment variables.")
    
    # Get credentials
    client_id = os.getenv('ZOHO_CLIENT_ID', '').strip()
    client_secret = os.getenv('ZOHO_CLIENT_SECRET', '').strip()
    access_token = os.getenv('ZOHO_ACCESS_TOKEN', '').strip()
    refresh_token = os.getenv('ZOHO_REFRESH_TOKEN', '').strip()
    
    print(f"\nCredential Status:")
    print(f"  Client ID: {client_id[:20] + '...' if client_id else 'MISSING'}")
    print(f"  Client Secret: {'FOUND' if client_secret else 'MISSING'}")
    print(f"  Access Token: {'FOUND' if access_token else 'MISSING'}")
    print(f"  Refresh Token: {'FOUND' if refresh_token else 'MISSING'}")
    
    # Validate tokens
    if access_token and not validate_token_format(access_token):
        print("Warning: Access token format appears invalid")
    
    # If no access token, show OAuth instructions
    if not access_token:
        if not client_id or not client_secret:
            print("\nERROR: Missing Client ID or Client Secret")
            print("Please add these to your .env file:")
            print("ZOHO_CLIENT_ID=your_client_id")
            print("ZOHO_CLIENT_SECRET=your_client_secret")
            return
        
        generate_oauth_instructions(client_id, client_secret)
        
        if refresh_token:
            print("\n" + "="*60)
            print("Alternative: Use Refresh Token")
            print("="*60)
            print("You have a refresh token. Generate new access token:")
            
            refresh_cmd = f'''curl -X POST "{ZOHO_TOKEN_URL}" \\
  -d "grant_type=refresh_token" \\
  -d "client_id={client_id}" \\
  -d "client_secret={client_secret}" \\
  -d "refresh_token={refresh_token}"'''
            
            print(f"\n{refresh_cmd}")
            print("\nThen update ZOHO_ACCESS_TOKEN in .env and run this script again")
        
        return
    
    # Run comprehensive API tests
    print("\n" + "="*60)
    print("Running Comprehensive API Tests")
    print("="*60)
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {},
        "modules_discovered": [],
        "course_related_fields": {},
        "sample_data": {}
    }
    
    # Test 1: Organization access
    org_success = test_organization(access_token)
    test_results["test_summary"]["organization"] = org_success
    
    if not org_success:
        print("\nAborting tests - Cannot access organization data")
        print("This usually means:")
        print("1. Access token is expired or invalid")
        print("2. Insufficient permissions")
        print("3. API connectivity issues")
        
        if refresh_token:
            print(f"\nTry refreshing your access token with:")
            refresh_cmd = f'''curl -X POST "{ZOHO_TOKEN_URL}" \\
  -d "grant_type=refresh_token" \\
  -d "client_id={client_id}" \\
  -d "client_secret={client_secret}" \\
  -d "refresh_token={refresh_token}"'''
            print(f"\n{refresh_cmd}")
        
        return
    
    # Test 2: Module discovery
    available_modules, custom_modules = discover_modules(access_token)
    test_results["modules_discovered"] = available_modules
    test_results["custom_modules"] = custom_modules
    test_results["test_summary"]["modules_discovered"] = len(available_modules)
    
    if not available_modules:
        print("\nNo modules found - this is unexpected")
        return
    
    # Test 3: Prioritized module analysis
    modules_to_test = []
    
    # Prioritize custom modules and course-relevant standard modules
    for module in PRIORITY_MODULES:
        if module in available_modules:
            modules_to_test.append(module)
    
    # Add some standard modules if we need more data
    for module in STANDARD_MODULES:
        if module in available_modules and len(modules_to_test) < 5:
            modules_to_test.append(module)
    
    print(f"\nTesting {len(modules_to_test)} priority modules for course feedback data")
    
    # Test each priority module
    for module in modules_to_test:
        # Analyze fields
        course_fields = analyze_module_fields(access_token, module)
        if course_fields:
            test_results["course_related_fields"][module] = course_fields
        
        # Test data access
        data_success, sample_records = test_module_data(access_token, module, limit=2)
        test_results["test_summary"][f"{module}_data_access"] = data_success
        
        if sample_records:
            test_results["sample_data"][module] = sample_records[:1]  # Save one sample
    
    # Test 4: COQL search for course data
    coql_success = test_coql_search(access_token)
    test_results["test_summary"]["coql_search"] = coql_success
    
    # Save results
    results_file = save_test_results(test_results)
    
    # Final summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len([k for k in test_results["test_summary"].keys() if isinstance(test_results["test_summary"][k], bool)])
    passed_tests = len([k for k, v in test_results["test_summary"].items() if v is True])
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Modules Discovered: {len(available_modules)}")
    print(f"Custom Modules: {len(custom_modules)}")
    
    course_field_count = sum(len(fields) for fields in test_results["course_related_fields"].values())
    print(f"Course-related Fields Found: {course_field_count}")
    
    if course_field_count > 0:
        print(f"\nCourse Feedback Data Sources Identified:")
        for module, fields in test_results["course_related_fields"].items():
            print(f"  {module}: {len(fields)} course-related fields")
    
    print(f"\nNext Steps for Course Aggregator:")
    print(f"1. Review detailed results in: {results_file}")
    print(f"2. Focus on modules with course-related fields")
    print(f"3. Build data extraction logic for identified modules")
    print(f"4. Implement Canvas + Zoho data aggregation")

if __name__ == "__main__":
    main()