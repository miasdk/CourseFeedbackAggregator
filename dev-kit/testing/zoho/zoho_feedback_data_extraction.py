#!/usr/bin/env python3
"""
Zoho CRM Course Feedback Data Extraction
Focused on extracting course feedback from accessible modules: Contacts, Deals, Accounts, Leads
Based on our discovered data structure
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

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

class ZohoCourseFeedbackExtractor:
    """Extract course feedback data from Zoho CRM"""
    
    def __init__(self):
        self.access_token = os.getenv('ZOHO_ACCESS_TOKEN')
        self.api_domain = 'https://www.zohoapis.com'
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}'
        }
        
        # Based on our discovery, these are the key modules with course feedback
        self.feedback_modules = {
            'Contacts': {
                'course_fields': [
                    'Program_Name', 'Official_Program_Name', 'Course_Completed',
                    'Programs', 'Type_of_Program', 'Program_Location', 'Program_Date'
                ],
                'feedback_fields': [
                    'Visitor_Score', 'Board_Member_Rating', 'IC_Reviewed'
                ],
                'student_fields': [
                    'Email', 'Full_Name', 'First_Name', 'Last_Name', 'Account_Name'
                ]
            },
            'Deals': {
                'course_fields': [
                    'Course_Name', 'Program', 'Course_Number', 'Course_Completed',
                    'Custom_Program_Group', 'Course_Term', 'Workshop'
                ],
                'feedback_fields': [
                    'Feedback_on_the_Content', 'Feedback_on_the_Faculty',
                    'Feedback_on_the_Activities_and_Exercises', 'Board_Member_Rating',
                    'Instructor_Review_Process', 'Completed_Course_Review', 'Houston_Review'
                ],
                'metadata_fields': [
                    'Deal_Name', 'Stage', 'Closing_Date', 'Amount'
                ]
            },
            'Accounts': {
                'course_fields': [
                    'Course_URL', 'Course_Number', 'ProgramName',
                    'Operational_Readiness_Program'
                ],
                'feedback_fields': [
                    'Rating'
                ],
                'org_fields': [
                    'Account_Name', 'Website', 'Industry'
                ]
            },
            'Leads': {
                'course_fields': [
                    'Program'
                ],
                'feedback_fields': [
                    'Visitor_Score'
                ],
                'student_fields': [
                    'Email', 'First_Name', 'Last_Name', 'Company'
                ]
            }
        }
    
    def extract_module_data(self, module_name: str, limit: int = 200) -> Dict:
        """Extract all relevant data from a module"""
        
        print(f"\n📊 Extracting data from {module_name} module...")
        
        all_records = []
        page = 1
        more_records = True
        
        while more_records and len(all_records) < limit:
            try:
                # Build request with pagination
                params = {
                    'page': page,
                    'per_page': min(200, limit - len(all_records))  # Max 200 per page
                }
                
                # Add specific fields if we know them
                if module_name in self.feedback_modules:
                    module_config = self.feedback_modules[module_name]
                    all_fields = []
                    for field_type in ['course_fields', 'feedback_fields', 'student_fields', 
                                      'metadata_fields', 'org_fields']:
                        if field_type in module_config:
                            all_fields.extend(module_config[field_type])
                    
                    # Add common fields
                    all_fields.extend(['id', 'Created_Time', 'Modified_Time', 'Owner'])
                    
                    # Request specific fields to reduce data size
                    params['fields'] = ','.join(all_fields)
                
                response = requests.get(
                    f"{self.api_domain}/crm/v2/{module_name}",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('data', [])
                    
                    if records:
                        all_records.extend(records)
                        print(f"   ✓ Page {page}: Retrieved {len(records)} records (Total: {len(all_records)})")
                        
                        # Check if there are more pages
                        info = data.get('info', {})
                        more_records = info.get('more_records', False)
                        page += 1
                    else:
                        more_records = False
                        
                elif response.status_code == 204:
                    print(f"   ℹ️  No more records in {module_name}")
                    more_records = False
                    
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
                    more_records = False
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                more_records = False
        
        return {
            'module': module_name,
            'record_count': len(all_records),
            'records': all_records
        }
    
    def analyze_feedback_data(self, module_data: Dict) -> Dict:
        """Analyze extracted data for course feedback patterns"""
        
        module_name = module_data['module']
        records = module_data['records']
        
        if not records:
            return {
                'module': module_name,
                'has_feedback': False,
                'feedback_count': 0
            }
        
        module_config = self.feedback_modules.get(module_name, {})
        
        # Analyze records
        feedback_records = []
        course_records = []
        
        for record in records:
            # Check for feedback data
            has_feedback = False
            feedback_data = {}
            
            # Extract feedback fields
            for field in module_config.get('feedback_fields', []):
                if field in record and record[field]:
                    has_feedback = True
                    feedback_data[field] = record[field]
            
            # Extract course fields
            course_data = {}
            for field in module_config.get('course_fields', []):
                if field in record and record[field]:
                    course_data[field] = record[field]
            
            # If has feedback or course data, store it
            if has_feedback:
                feedback_record = {
                    'id': record.get('id'),
                    'feedback': feedback_data,
                    'course': course_data,
                    'created': record.get('Created_Time'),
                    'modified': record.get('Modified_Time')
                }
                
                # Add student/contact info
                for field in module_config.get('student_fields', []):
                    if field in record and record[field]:
                        feedback_record[field.lower()] = record[field]
                
                feedback_records.append(feedback_record)
            
            if course_data:
                course_records.append(course_data)
        
        return {
            'module': module_name,
            'has_feedback': len(feedback_records) > 0,
            'feedback_count': len(feedback_records),
            'course_count': len(course_records),
            'feedback_records': feedback_records[:10],  # Sample of feedback records
            'unique_courses': self.extract_unique_courses(course_records),
            'feedback_fields_used': list(set([field for r in feedback_records for field in r.get('feedback', {}).keys()]))
        }
    
    def extract_unique_courses(self, course_records: List[Dict]) -> List[str]:
        """Extract unique course names from records"""
        
        courses = set()
        
        for record in course_records:
            for field, value in record.items():
                if value and isinstance(value, str):
                    # Clean and add course name
                    course_name = str(value).strip()
                    if course_name and len(course_name) > 2:
                        courses.add(course_name)
        
        return sorted(list(courses))[:20]  # Return top 20 courses
    
    def create_unified_schema(self, all_feedback_data: List[Dict]) -> Dict:
        """Create a unified schema mapping for course feedback"""
        
        print("\n🔄 Creating unified schema mapping...")
        
        unified_records = []
        
        for module_analysis in all_feedback_data:
            if not module_analysis['has_feedback']:
                continue
            
            module_name = module_analysis['module']
            
            for record in module_analysis.get('feedback_records', []):
                # Map to unified schema
                unified_record = {
                    'source_system': 'Zoho CRM',
                    'source_module': module_name,
                    'source_id': record.get('id'),
                    'course_name': None,
                    'course_id': None,
                    'student_email': None,
                    'student_name': None,
                    'rating': None,
                    'feedback_text': None,
                    'feedback_date': record.get('created') or record.get('modified'),
                    'priority': None,
                    'category': None,
                    'raw_feedback': record.get('feedback', {})
                }
                
                # Map course name
                course_fields = record.get('course', {})
                for field in ['Course_Name', 'Program_Name', 'Official_Program_Name', 'ProgramName', 'Program']:
                    if field in course_fields:
                        unified_record['course_name'] = course_fields[field]
                        break
                
                # Map student info
                unified_record['student_email'] = record.get('email')
                unified_record['student_name'] = record.get('full_name') or f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()
                
                # Map feedback/rating
                feedback = record.get('feedback', {})
                
                # Try to extract rating
                for rating_field in ['Rating', 'Board_Member_Rating', 'Visitor_Score']:
                    if rating_field in feedback:
                        try:
                            unified_record['rating'] = float(feedback[rating_field])
                            break
                        except:
                            pass
                
                # Try to extract feedback text
                text_fields = []
                for field in ['Feedback_on_the_Content', 'Feedback_on_the_Faculty', 
                            'Feedback_on_the_Activities_and_Exercises', 'Houston_Review']:
                    if field in feedback and feedback[field]:
                        text_fields.append(f"{field.replace('_', ' ')}: {feedback[field]}")
                
                if text_fields:
                    unified_record['feedback_text'] = ' | '.join(text_fields)
                
                unified_records.append(unified_record)
        
        return {
            'total_feedback_records': len(unified_records),
            'unified_records': unified_records,
            'schema_mapping': {
                'Contacts': {
                    'course_name': ['Program_Name', 'Official_Program_Name'],
                    'rating': ['Board_Member_Rating', 'Visitor_Score'],
                    'student_email': 'Email',
                    'student_name': 'Full_Name'
                },
                'Deals': {
                    'course_name': ['Course_Name', 'Program'],
                    'feedback_text': ['Feedback_on_the_Content', 'Feedback_on_the_Faculty'],
                    'rating': 'Board_Member_Rating'
                },
                'Accounts': {
                    'course_name': 'ProgramName',
                    'rating': 'Rating',
                    'organization': 'Account_Name'
                },
                'Leads': {
                    'course_name': 'Program',
                    'rating': 'Visitor_Score',
                    'student_email': 'Email'
                }
            }
        }
    
    def run_extraction(self) -> Dict:
        """Run the complete extraction process"""
        
        print("="*60)
        print("🚀 ZOHO CRM COURSE FEEDBACK EXTRACTION")
        print("="*60)
        
        extraction_report = {
            'timestamp': datetime.now().isoformat(),
            'modules_processed': [],
            'total_records': 0,
            'feedback_analysis': [],
            'unified_schema': {},
            'recommendations': []
        }
        
        # Extract data from each module
        for module_name in self.feedback_modules.keys():
            print(f"\nProcessing {module_name}...")
            
            # Extract data
            module_data = self.extract_module_data(module_name, limit=200)
            extraction_report['modules_processed'].append(module_name)
            extraction_report['total_records'] += module_data['record_count']
            
            # Analyze feedback
            analysis = self.analyze_feedback_data(module_data)
            extraction_report['feedback_analysis'].append(analysis)
            
            if analysis['has_feedback']:
                print(f"   ✅ Found {analysis['feedback_count']} feedback records")
                print(f"   📚 Courses: {', '.join(analysis['unique_courses'][:5])}...")
        
        # Create unified schema
        extraction_report['unified_schema'] = self.create_unified_schema(
            extraction_report['feedback_analysis']
        )
        
        # Generate recommendations
        extraction_report['recommendations'] = self.generate_recommendations(
            extraction_report['feedback_analysis']
        )
        
        return extraction_report
    
    def generate_recommendations(self, feedback_analysis: List[Dict]) -> List[str]:
        """Generate integration recommendations based on analysis"""
        
        recommendations = []
        
        # Find which module has the most feedback
        best_module = None
        max_feedback = 0
        
        for analysis in feedback_analysis:
            if analysis['feedback_count'] > max_feedback:
                max_feedback = analysis['feedback_count']
                best_module = analysis['module']
        
        if best_module:
            recommendations.append(f"Primary feedback source: {best_module} module ({max_feedback} records)")
        
        # Check for specific feedback types
        for analysis in feedback_analysis:
            if 'Feedback_on_the_Content' in analysis.get('feedback_fields_used', []):
                recommendations.append(f"Content feedback available in {analysis['module']} module")
            if 'Feedback_on_the_Faculty' in analysis.get('feedback_fields_used', []):
                recommendations.append(f"Faculty feedback available in {analysis['module']} module")
            if 'Board_Member_Rating' in analysis.get('feedback_fields_used', []):
                recommendations.append(f"Board ratings available in {analysis['module']} module")
        
        return recommendations
    
    def save_results(self, report: Dict):
        """Save extraction results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full report
        report_filename = f"zoho_extraction_report_{timestamp}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Full report saved to: {report_filename}")
        
        # Save unified records for backend integration
        if report.get('unified_schema', {}).get('unified_records'):
            unified_filename = f"zoho_unified_feedback_{timestamp}.json"
            unified_data = {
                'source': 'Zoho CRM',
                'extraction_date': report['timestamp'],
                'record_count': report['unified_schema']['total_feedback_records'],
                'schema_version': '1.0',
                'records': report['unified_schema']['unified_records']
            }
            with open(unified_filename, 'w') as f:
                json.dump(unified_data, f, indent=2, default=str)
            print(f"📋 Unified feedback data saved to: {unified_filename}")

def main():
    """Run the Zoho course feedback extraction"""
    
    extractor = ZohoCourseFeedbackExtractor()
    
    # Run extraction
    report = extractor.run_extraction()
    
    # Save results
    extractor.save_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 EXTRACTION SUMMARY")
    print("="*60)
    print(f"✅ Modules processed: {len(report['modules_processed'])}")
    print(f"✅ Total records analyzed: {report['total_records']}")
    print(f"✅ Feedback records found: {report['unified_schema'].get('total_feedback_records', 0)}")
    
    if report['recommendations']:
        print("\n🎯 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

if __name__ == "__main__":
    main()