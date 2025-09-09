#!/usr/bin/env python3
"""
Zoho Analytics API Discovery for Course Feedback Insights
Documentation: https://www.zoho.com/analytics/api/
API Base URL: https://analyticsapi.zoho.com/restapi/v2/

Zoho Analytics (formerly Zoho Reports) provides:
- Pre-built dashboards and reports
- Data visualization and insights
- Integration with CRM, Survey, and other Zoho apps
- Custom analytics and trend analysis
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

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

class ZohoAnalyticsDiscovery:
    """Discover course analytics and insights in Zoho Analytics"""
    
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.access_token = os.getenv('ZOHO_ACCESS_TOKEN')
        
        # Zoho Analytics API endpoints
        self.analytics_api_bases = [
            'https://analyticsapi.zoho.com/restapi/v2',
            'https://analytics.zoho.com/api/v2',
            'https://www.zohoapis.com/analytics/v2'
        ]
        self.accounts_url = 'https://accounts.zoho.com'
        
        self.headers = {}
        
        # Course analytics keywords
        self.analytics_keywords = [
            'course', 'program', 'training', 'student', 'enrollment',
            'feedback', 'rating', 'performance', 'completion',
            'satisfaction', 'survey', 'evaluation'
        ]
    
    def refresh_access_token_for_analytics(self) -> bool:
        """Refresh access token with Analytics API scope"""
        
        if self.access_token:
            self.headers = {
                'Authorization': f'Zoho-oauthtoken {self.access_token}'
            }
            print("✅ Using existing access token for Analytics API")
            return True
        
        # Analytics API requires specific scope: ZohoAnalytics.data.read, ZohoAnalytics.fullaccess
        token_url = f"{self.accounts_url}/oauth/v2/token"
        
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
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
                print("✅ Access token refreshed for Analytics API")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error refreshing token: {str(e)}")
            return False
    
    def test_analytics_api_connection(self) -> bool:
        """Test connection to Zoho Analytics API"""
        
        print("\n🔌 Testing Analytics API connection...")
        
        for i, base_url in enumerate(self.analytics_api_bases):
            print(f"\nTesting base URL {i+1}: {base_url}")
            
            test_endpoints = [
                ('workspaces', f"{base_url}/workspaces"),
                ('orgs', f"{base_url}/orgs"),
                ('metadata', f"{base_url}/metadata"),
                ('user', f"{base_url}/user")
            ]
            
            for endpoint_name, endpoint_url in test_endpoints:
                try:
                    response = requests.get(endpoint_url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Connected to Analytics API: {endpoint_name}")
                        data = response.json()
                        
                        if 'data' in data:
                            print(f"   Found data: {type(data['data'])}")
                            if isinstance(data['data'], list):
                                print(f"   Items count: {len(data['data'])}")
                        else:
                            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        
                        # Store working base URL
                        self.working_api_base = base_url
                        return True
                        
                    elif response.status_code == 401:
                        error_data = response.json() if response.content else {}
                        error_code = error_data.get('errorCode', 'UNKNOWN')
                        print(f"   ❌ {endpoint_name}: {error_code} - {error_data.get('message', 'Unauthorized')}")
                        
                    elif response.status_code == 403:
                        print(f"   ❌ {endpoint_name}: Access forbidden (scope issue)")
                        
                    elif response.status_code == 404:
                        print(f"   ⚠️  {endpoint_name}: Not found")
                        
                    else:
                        print(f"   ⚠️  {endpoint_name}: Status {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print(f"   ⏰ {endpoint_name}: Timeout")
                except requests.exceptions.ConnectionError:
                    print(f"   🚫 {endpoint_name}: Connection failed")
                except Exception as e:
                    print(f"   ❌ {endpoint_name}: {str(e)[:50]}...")
        
        return False
    
    def discover_workspaces(self) -> List[Dict]:
        """Discover Analytics workspaces that might contain course data"""
        
        print(f"\n📊 Discovering Analytics workspaces...")
        
        if not hasattr(self, 'working_api_base'):
            print("❌ No working API base found. Run test_analytics_api_connection first.")
            return []
        
        try:
            endpoint = f"{self.working_api_base}/workspaces"
            response = requests.get(endpoint, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('data', [])
                
                print(f"✅ Found {len(workspaces)} workspaces")
                
                # Filter for course-related workspaces
                course_workspaces = []
                
                for workspace in workspaces:
                    workspace_name = workspace.get('workspaceName', '').lower()
                    workspace_desc = workspace.get('description', '').lower()
                    
                    # Check if workspace is course-related
                    is_course_related = any(keyword in workspace_name or keyword in workspace_desc 
                                          for keyword in self.analytics_keywords)
                    
                    workspace_info = {
                        'workspace_id': workspace.get('workspaceId'),
                        'workspace_name': workspace.get('workspaceName'),
                        'description': workspace.get('description'),
                        'owner_name': workspace.get('ownerName'),
                        'created_time': workspace.get('createdTime'),
                        'is_course_related': is_course_related,
                        'view_count': workspace.get('viewCount', 0)
                    }
                    
                    if is_course_related:
                        course_workspaces.append(workspace_info)
                        print(f"   📚 Course Workspace: {workspace.get('workspaceName')}")
                    else:
                        # Also include high-activity workspaces that might contain course data
                        if workspace.get('viewCount', 0) > 100:
                            workspace_info['is_course_related'] = 'high_activity'
                            course_workspaces.append(workspace_info)
                            print(f"   📈 High-Activity Workspace: {workspace.get('workspaceName')} ({workspace.get('viewCount', 0)} views)")
                
                print(f"\n✅ Found {len(course_workspaces)} potentially relevant workspaces")
                return course_workspaces
                
            else:
                print(f"❌ Failed to get workspaces: {response.status_code}")
                print(response.text[:500])
                return []
                
        except Exception as e:
            print(f"❌ Error discovering workspaces: {str(e)}")
            return []
    
    def get_workspace_details(self, workspace_id: str) -> Dict:
        """Get detailed information about a workspace"""
        
        print(f"\n🔍 Getting details for workspace: {workspace_id}")
        
        try:
            # Get tables/views in workspace
            tables_endpoint = f"{self.working_api_base}/workspaces/{workspace_id}/tables"
            tables_response = requests.get(tables_endpoint, headers=self.headers)
            
            workspace_details = {
                'workspace_id': workspace_id,
                'tables': [],
                'views': [],
                'course_related_items': []
            }
            
            if tables_response.status_code == 200:
                tables_data = tables_response.json()
                tables = tables_data.get('data', [])
                
                workspace_details['tables'] = tables
                print(f"   ✅ Found {len(tables)} tables/views")
                
                # Analyze tables for course content
                for table in tables:
                    table_name = table.get('tableName', '').lower()
                    table_desc = table.get('description', '').lower()
                    
                    # Check if table contains course/feedback data
                    is_course_related = any(keyword in table_name or keyword in table_desc
                                          for keyword in self.analytics_keywords)
                    
                    if is_course_related:
                        course_item = {
                            'table_id': table.get('tableId'),
                            'table_name': table.get('tableName'),
                            'description': table.get('description'),
                            'row_count': table.get('rowCount', 0),
                            'column_count': table.get('columnCount', 0),
                            'type': table.get('type', 'table')
                        }
                        workspace_details['course_related_items'].append(course_item)
                        print(f"      📋 Course Table: {table.get('tableName')} ({table.get('rowCount', 0)} rows)")
                
            else:
                print(f"   ⚠️  Could not get tables: {tables_response.status_code}")
            
            return workspace_details
            
        except Exception as e:
            print(f"   ❌ Error getting workspace details: {str(e)}")
            return {}
    
    def get_table_data_sample(self, workspace_id: str, table_id: str, limit: int = 10) -> Dict:
        """Get sample data from a table to understand structure"""
        
        print(f"\n📊 Getting sample data from table: {table_id}")
        
        try:
            # Get table data using SQL API or data export
            data_endpoint = f"{self.working_api_base}/workspaces/{workspace_id}/tables/{table_id}/data"
            
            params = {
                'limit': limit,
                'offset': 0
            }
            
            response = requests.get(data_endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                rows = data.get('data', {}).get('rows', [])
                columns = data.get('data', {}).get('columns', [])
                
                print(f"   ✅ Retrieved {len(rows)} rows, {len(columns)} columns")
                
                # Analyze columns for feedback patterns
                feedback_columns = []
                course_columns = []
                
                for col in columns:
                    col_name = col.get('columnName', '').lower()
                    
                    if any(keyword in col_name for keyword in ['rating', 'score', 'feedback', 'review', 'satisfaction']):
                        feedback_columns.append(col)
                    elif any(keyword in col_name for keyword in ['course', 'program', 'training']):
                        course_columns.append(col)
                
                return {
                    'table_id': table_id,
                    'sample_rows': rows[:5],  # First 5 rows as sample
                    'columns': columns,
                    'feedback_columns': feedback_columns,
                    'course_columns': course_columns,
                    'has_course_feedback': len(feedback_columns) > 0 and len(course_columns) > 0
                }
                
            elif response.status_code == 403:
                print(f"   ❌ Access forbidden - might need additional Analytics permissions")
                return {}
            else:
                print(f"   ⚠️  Could not get data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"   ❌ Error getting table data: {str(e)}")
            return {}
    
    def search_for_course_analytics(self) -> Dict:
        """Search for existing course analytics and reports"""
        
        print(f"\n🔎 Searching for course analytics...")
        
        # Try to find pre-built reports or dashboards
        try:
            # Search for reports/dashboards
            search_endpoints = [
                ('reports', f"{self.working_api_base}/reports"),
                ('dashboards', f"{self.working_api_base}/dashboards"),
                ('views', f"{self.working_api_base}/views")
            ]
            
            analytics_found = {}
            
            for item_type, endpoint in search_endpoints:
                try:
                    response = requests.get(endpoint, headers=self.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('data', [])
                        
                        # Filter for course-related items
                        course_items = []
                        for item in items:
                            item_name = item.get('name', '').lower()
                            if any(keyword in item_name for keyword in self.analytics_keywords):
                                course_items.append(item)
                        
                        if course_items:
                            analytics_found[item_type] = course_items
                            print(f"   ✅ Found {len(course_items)} course-related {item_type}")
                    
                except Exception as e:
                    print(f"   ⚠️  Error searching {item_type}: {str(e)[:50]}")
            
            return analytics_found
            
        except Exception as e:
            print(f"   ❌ Error searching for analytics: {str(e)}")
            return {}
    
    def run_analytics_discovery(self) -> Dict:
        """Run complete Analytics API discovery"""
        
        print("="*60)
        print("📊 ZOHO ANALYTICS API DISCOVERY")
        print("="*60)
        
        discovery_report = {
            'timestamp': datetime.now().isoformat(),
            'api_connection': False,
            'workspaces_found': 0,
            'course_workspaces': [],
            'workspace_details': {},
            'sample_data': {},
            'existing_analytics': {},
            'recommendations': []
        }
        
        # 1. Authenticate and test connection
        if not self.refresh_access_token_for_analytics():
            discovery_report['error'] = "Authentication failed"
            return discovery_report
        
        if not self.test_analytics_api_connection():
            discovery_report['error'] = "Could not connect to Analytics API - check scopes"
            return discovery_report
        
        discovery_report['api_connection'] = True
        
        # 2. Discover workspaces
        workspaces = self.discover_workspaces()
        discovery_report['workspaces_found'] = len(workspaces)
        discovery_report['course_workspaces'] = workspaces
        
        if not workspaces:
            discovery_report['recommendations'].append("No course-related workspaces found")
            return discovery_report
        
        # 3. Analyze top workspaces
        print(f"\n📋 Analyzing top {min(3, len(workspaces))} workspaces...")
        
        for workspace in workspaces[:3]:
            workspace_id = workspace['workspace_id']
            
            # Get workspace structure
            details = self.get_workspace_details(workspace_id)
            discovery_report['workspace_details'][workspace_id] = details
            
            # Get sample data from course-related tables
            for item in details.get('course_related_items', [])[:2]:  # Top 2 tables per workspace
                table_id = item['table_id']
                sample = self.get_table_data_sample(workspace_id, table_id)
                if sample:
                    discovery_report['sample_data'][f"{workspace_id}_{table_id}"] = sample
        
        # 4. Search for existing analytics
        existing_analytics = self.search_for_course_analytics()
        discovery_report['existing_analytics'] = existing_analytics
        
        # 5. Generate recommendations
        discovery_report['recommendations'] = self.generate_analytics_recommendations(discovery_report)
        
        return discovery_report
    
    def generate_analytics_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations for Analytics API integration"""
        
        recommendations = []
        
        if report['workspaces_found'] > 0:
            recommendations.append(f"Found {report['workspaces_found']} potentially relevant workspaces")
            
            # Check for course data
            total_course_tables = 0
            for details in report.get('workspace_details', {}).values():
                total_course_tables += len(details.get('course_related_items', []))
            
            if total_course_tables > 0:
                recommendations.append(f"Found {total_course_tables} course-related tables/views")
        
        # Check for existing analytics
        for analytics_type, items in report.get('existing_analytics', {}).items():
            if items:
                recommendations.append(f"Found {len(items)} existing course {analytics_type}")
        
        # Check for feedback data
        has_feedback_data = False
        for sample in report.get('sample_data', {}).values():
            if sample.get('has_course_feedback'):
                has_feedback_data = True
                break
        
        if has_feedback_data:
            recommendations.append("Found tables with both course and feedback columns")
            recommendations.append("Analytics API integration recommended for trend analysis")
        
        # Strategic recommendations
        if report['workspaces_found'] > 0:
            recommendations.append("Use Analytics API for aggregated insights and reporting")
            recommendations.append("Combine with CRM data for comprehensive feedback analysis")
        
        return recommendations
    
    def save_results(self, report: Dict):
        """Save discovery results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"zoho_analytics_discovery_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Analytics discovery report saved to: {filename}")
        
        # Create integration recommendations if analytics found
        if report.get('course_workspaces'):
            integration_guide = {
                'analytics_integration': {
                    'base_url': getattr(self, 'working_api_base', 'https://analyticsapi.zoho.com/restapi/v2'),
                    'authentication': 'Zoho OAuth 2.0',
                    'required_scopes': ['ZohoAnalytics.data.read', 'ZohoAnalytics.fullaccess'],
                    'primary_endpoints': {
                        'workspaces': '/workspaces',
                        'tables': '/workspaces/{workspace_id}/tables',
                        'data': '/workspaces/{workspace_id}/tables/{table_id}/data'
                    },
                    'course_workspaces': [
                        {
                            'workspace_id': w['workspace_id'],
                            'workspace_name': w['workspace_name'],
                            'course_related': w['is_course_related']
                        }
                        for w in report['course_workspaces']
                    ],
                    'use_cases': [
                        'Trend analysis of course feedback over time',
                        'Aggregated satisfaction scores by program',
                        'Instructor performance analytics',
                        'Course completion and engagement metrics',
                        'Cross-program comparison dashboards'
                    ],
                    'integration_priority': 'medium'  # After CRM integration
                }
            }
            
            guide_filename = f"zoho_analytics_integration_guide_{timestamp}.json"
            with open(guide_filename, 'w') as f:
                json.dump(integration_guide, f, indent=2)
            print(f"📋 Integration guide saved to: {guide_filename}")

def main():
    """Run the Analytics API discovery"""
    
    discovery = ZohoAnalyticsDiscovery()
    
    # Run discovery
    report = discovery.run_analytics_discovery()
    
    # Save results
    discovery.save_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ANALYTICS DISCOVERY SUMMARY")
    print("="*60)
    
    if report.get('error'):
        print(f"❌ Discovery failed: {report['error']}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check if Analytics API scope is included in OAuth token")
        print("   2. Required scopes: ZohoAnalytics.data.read, ZohoAnalytics.fullaccess")
        print("   3. Analytics API uses separate permissions from CRM API")
    else:
        print(f"✅ API Connection: {report['api_connection']}")
        print(f"✅ Workspaces Found: {report['workspaces_found']}")
        
        # Count total tables
        total_tables = sum(
            len(details.get('course_related_items', []))
            for details in report.get('workspace_details', {}).values()
        )
        print(f"✅ Course-Related Tables: {total_tables}")
        
        if report.get('recommendations'):
            print(f"\n🎯 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")

if __name__ == "__main__":
    main()