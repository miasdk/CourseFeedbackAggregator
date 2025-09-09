#!/usr/bin/env python3
"""
Zoho Survey API Discovery for Course Feedback
Documentation: https://www.zoho.com/survey/api/
API Base URL: https://surveyapi.zoho.com/zsapi/v2/
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

class ZohoSurveyDiscovery:
    """Discover course surveys and responses in Zoho Survey"""
    
    def __init__(self):
        self.client_id = os.getenv('ZOHO_CLIENT_ID')
        self.client_secret = os.getenv('ZOHO_CLIENT_SECRET')
        self.refresh_token = os.getenv('ZOHO_REFRESH_TOKEN')
        self.access_token = os.getenv('ZOHO_ACCESS_TOKEN')
        
        # Zoho Survey API endpoints (based on data center)
        # Common patterns: survey.zoho.com, survey.zoho.in, survey.zoho.eu, etc.
        self.survey_api_bases = [
            'https://survey.zoho.com/survey/api/v1',
            'https://survey.zoho.com/api/v1',
            'https://www.zohoapis.com/survey/v1',
            'https://survey.zohoapis.com/v1'
        ]
        self.accounts_url = 'https://accounts.zoho.com'
        
        self.headers = {}
        
        # Course-related keywords to look for in surveys
        self.course_keywords = [
            'course', 'program', 'training', 'workshop', 'session',
            'learning', 'education', 'class', 'curriculum', 'module',
            'leadership', 'ai', 'strategic', 'customer', 'experience'
        ]
    
    def refresh_access_token_for_survey(self) -> bool:
        """Refresh access token with Survey API scope"""
        
        if self.access_token:
            self.headers = {
                'Authorization': f'Zoho-oauthtoken {self.access_token}'
            }
            print("✅ Using existing access token for Survey API")
            return True
        
        # Note: Survey API might require different scope than CRM
        # Scope should include: ZohoSurvey.surveys.READ, ZohoSurvey.responses.READ
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
                print("✅ Access token refreshed for Survey API")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error refreshing token: {str(e)}")
            return False
    
    def test_survey_api_connection(self) -> bool:
        """Test connection to Zoho Survey API with different base URLs"""
        
        print("\n🔌 Testing Survey API connection...")
        
        # Test different base URLs and endpoints
        for i, base_url in enumerate(self.survey_api_bases):
            print(f"\nTesting base URL {i+1}: {base_url}")
            
            test_endpoints = [
                ('surveys', f"{base_url}/surveys"),
                ('userinfos', f"{base_url}/userinfos"),
                ('private/userinfos', f"{base_url}/private/userinfos"),
                ('public/surveys', f"{base_url}/public/surveys")
            ]
            
            for endpoint_name, endpoint_url in test_endpoints:
                try:
                    response = requests.get(endpoint_url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Connected to Survey API: {endpoint_name}")
                        data = response.json()
                        if 'surveys' in data:
                            print(f"   Found {len(data['surveys'])} surveys")
                        elif 'data' in data:
                            print(f"   Found data: {type(data['data'])}")
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
    
    def discover_surveys(self, api_version='v1') -> List[Dict]:
        """Discover all surveys, focusing on course-related ones"""
        
        print(f"\n📋 Discovering surveys...")
        
        if not hasattr(self, 'working_api_base'):
            print("❌ No working API base found. Run test_survey_api_connection first.")
            return []
        
        try:
            endpoint = f"{self.working_api_base}/surveys"
            response = requests.get(endpoint, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                all_surveys = data.get('surveys', [])
                
                print(f"✅ Found {len(all_surveys)} total surveys")
                
                # Filter for course-related surveys
                course_surveys = []
                
                for survey in all_surveys:
                    survey_name = survey.get('surveyName', '').lower()
                    survey_desc = survey.get('description', '').lower()
                    
                    # Check if survey is course-related
                    is_course_related = any(keyword in survey_name or keyword in survey_desc 
                                          for keyword in self.course_keywords)
                    
                    survey_info = {
                        'survey_id': survey.get('surveyId'),
                        'survey_name': survey.get('surveyName'),
                        'description': survey.get('description'),
                        'status': survey.get('status'),
                        'created_time': survey.get('createdTime'),
                        'response_count': survey.get('responseCount', 0),
                        'question_count': survey.get('questionCount', 0),
                        'is_course_related': is_course_related
                    }
                    
                    if is_course_related:
                        course_surveys.append(survey_info)
                        print(f"   📚 Course Survey: {survey.get('surveyName')} ({survey.get('responseCount', 0)} responses)")
                
                print(f"\n✅ Found {len(course_surveys)} course-related surveys")
                return course_surveys
                
            else:
                print(f"❌ Failed to get surveys: {response.status_code}")
                print(response.text[:500])
                return []
                
        except Exception as e:
            print(f"❌ Error discovering surveys: {str(e)}")
            return []
    
    def get_survey_details(self, survey_id: str, api_version='v2') -> Dict:
        """Get detailed information about a specific survey"""
        
        print(f"\n🔍 Getting details for survey: {survey_id}")
        
        try:
            # Get survey questions
            questions_endpoint = f"{self.survey_api_base}/{api_version}/surveys/{survey_id}/questions"
            questions_response = requests.get(questions_endpoint, headers=self.headers)
            
            survey_details = {
                'survey_id': survey_id,
                'questions': [],
                'question_count': 0,
                'feedback_questions': []
            }
            
            if questions_response.status_code == 200:
                questions_data = questions_response.json()
                questions = questions_data.get('questions', [])
                
                survey_details['questions'] = questions
                survey_details['question_count'] = len(questions)
                
                # Analyze questions for feedback patterns
                feedback_questions = []
                
                for question in questions:
                    question_text = question.get('questionText', '').lower()
                    question_type = question.get('questionType', '')
                    
                    # Check if question is feedback-related
                    is_feedback = any(keyword in question_text for keyword in 
                                    ['rate', 'rating', 'feedback', 'comment', 'opinion', 
                                     'satisfaction', 'recommend', 'improve', 'thoughts'])
                    
                    question_info = {
                        'question_id': question.get('questionId'),
                        'question_text': question.get('questionText'),
                        'question_type': question_type,
                        'is_feedback': is_feedback,
                        'is_required': question.get('isMandatory', False)
                    }
                    
                    if is_feedback:
                        feedback_questions.append(question_info)
                
                survey_details['feedback_questions'] = feedback_questions
                print(f"   ✅ Found {len(questions)} questions, {len(feedback_questions)} feedback questions")
                
            else:
                print(f"   ⚠️  Could not get questions: {questions_response.status_code}")
            
            return survey_details
            
        except Exception as e:
            print(f"   ❌ Error getting survey details: {str(e)}")
            return {}
    
    def get_survey_responses(self, survey_id: str, limit: int = 50, api_version='v2') -> Dict:
        """Get responses for a survey"""
        
        print(f"\n📊 Getting responses for survey: {survey_id}")
        
        try:
            # Get survey responses
            responses_endpoint = f"{self.survey_api_base}/{api_version}/surveys/{survey_id}/responses"
            
            params = {
                'limit': min(limit, 100),  # API might have limits
                'offset': 0
            }
            
            response = requests.get(responses_endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                responses = data.get('responses', [])
                
                print(f"   ✅ Retrieved {len(responses)} responses")
                
                # Analyze responses for feedback content
                feedback_responses = []
                
                for resp in responses:
                    response_info = {
                        'response_id': resp.get('responseId'),
                        'submitted_time': resp.get('submittedTime'),
                        'completion_time': resp.get('completionTime'),
                        'answers': resp.get('answers', []),
                        'respondent_info': resp.get('respondentInfo', {}),
                        'has_feedback': False,
                        'feedback_content': []
                    }
                    
                    # Extract feedback from answers
                    for answer in resp.get('answers', []):
                        answer_text = str(answer.get('answerText', '')).lower()
                        
                        # Check if answer contains meaningful feedback
                        if len(answer_text) > 10:  # Substantive answers
                            response_info['has_feedback'] = True
                            response_info['feedback_content'].append({
                                'question_id': answer.get('questionId'),
                                'answer_text': answer.get('answerText'),
                                'answer_type': answer.get('answerType')
                            })
                    
                    if response_info['has_feedback']:
                        feedback_responses.append(response_info)
                
                print(f"   ✅ Found {len(feedback_responses)} responses with feedback content")
                
                return {
                    'survey_id': survey_id,
                    'total_responses': len(responses),
                    'feedback_responses': feedback_responses[:10],  # Sample
                    'all_responses': responses
                }
                
            elif response.status_code == 403:
                print(f"   ❌ Access forbidden - might need additional Survey API permissions")
                return {}
            else:
                print(f"   ⚠️  Could not get responses: {response.status_code}")
                print(response.text[:200])
                return {}
                
        except Exception as e:
            print(f"   ❌ Error getting responses: {str(e)}")
            return {}
    
    def run_survey_discovery(self) -> Dict:
        """Run complete Survey API discovery"""
        
        print("="*60)
        print("🚀 ZOHO SURVEY API DISCOVERY")
        print("="*60)
        
        discovery_report = {
            'timestamp': datetime.now().isoformat(),
            'api_connection': False,
            'surveys_found': 0,
            'course_surveys': [],
            'survey_details': {},
            'response_data': {},
            'recommendations': []
        }
        
        # 1. Authenticate and test connection
        if not self.refresh_access_token_for_survey():
            discovery_report['error'] = "Authentication failed"
            return discovery_report
        
        if not self.test_survey_api_connection():
            discovery_report['error'] = "Could not connect to Survey API - check scopes"
            return discovery_report
        
        discovery_report['api_connection'] = True
        
        # 2. Discover surveys
        course_surveys = self.discover_surveys()
        discovery_report['surveys_found'] = len(course_surveys)
        discovery_report['course_surveys'] = course_surveys
        
        if not course_surveys:
            discovery_report['recommendations'].append("No course surveys found - check survey naming or keywords")
            return discovery_report
        
        # 3. Get detailed info for top surveys
        print(f"\n📋 Analyzing top {min(3, len(course_surveys))} course surveys...")
        
        for survey in course_surveys[:3]:  # Analyze top 3 surveys
            survey_id = survey['survey_id']
            
            # Get survey structure
            details = self.get_survey_details(survey_id)
            discovery_report['survey_details'][survey_id] = details
            
            # Get sample responses if available
            if survey.get('response_count', 0) > 0:
                responses = self.get_survey_responses(survey_id, limit=20)
                discovery_report['response_data'][survey_id] = responses
        
        # 4. Generate recommendations
        discovery_report['recommendations'] = self.generate_survey_recommendations(discovery_report)
        
        return discovery_report
    
    def generate_survey_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations for Survey API integration"""
        
        recommendations = []
        
        if report['surveys_found'] > 0:
            recommendations.append(f"Found {report['surveys_found']} course-related surveys")
            
            # Check for surveys with responses
            surveys_with_responses = [s for s in report['course_surveys'] if s.get('response_count', 0) > 0]
            if surveys_with_responses:
                recommendations.append(f"{len(surveys_with_responses)} surveys have response data")
                
                # Find survey with most responses
                top_survey = max(surveys_with_responses, key=lambda x: x.get('response_count', 0))
                recommendations.append(f"Primary survey: '{top_survey['survey_name']}' ({top_survey['response_count']} responses)")
        
        # Check for feedback questions
        total_feedback_questions = 0
        for details in report.get('survey_details', {}).values():
            total_feedback_questions += len(details.get('feedback_questions', []))
        
        if total_feedback_questions > 0:
            recommendations.append(f"Found {total_feedback_questions} feedback-specific questions across surveys")
        
        # Check for response data
        total_feedback_responses = 0
        for responses in report.get('response_data', {}).values():
            feedback_responses = responses.get('feedback_responses', [])
            total_feedback_responses += len(feedback_responses)
        
        if total_feedback_responses > 0:
            recommendations.append(f"Found {total_feedback_responses} responses with substantial feedback content")
            recommendations.append("Survey API integration recommended as primary source for course feedback")
        
        return recommendations
    
    def save_results(self, report: Dict):
        """Save discovery results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full report
        report_filename = f"zoho_survey_discovery_{timestamp}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Survey discovery report saved to: {report_filename}")
        
        # Create integration guide if surveys found
        if report.get('course_surveys'):
            integration_guide = {
                'survey_api_integration': {
                    'base_url': self.survey_api_base,
                    'recommended_version': 'v2',
                    'authentication': 'Zoho OAuth 2.0',
                    'required_scopes': ['ZohoSurvey.surveys.READ', 'ZohoSurvey.responses.READ'],
                    'primary_endpoints': {
                        'surveys_list': '/surveys',
                        'survey_questions': '/surveys/{survey_id}/questions',
                        'survey_responses': '/surveys/{survey_id}/responses'
                    },
                    'course_surveys': [
                        {
                            'survey_id': s['survey_id'],
                            'survey_name': s['survey_name'],
                            'response_count': s['response_count']
                        }
                        for s in report['course_surveys']
                    ],
                    'polling_frequency': 'weekly',
                    'implementation_priority': 'high'
                }
            }
            
            guide_filename = f"zoho_survey_integration_guide_{timestamp}.json"
            with open(guide_filename, 'w') as f:
                json.dump(integration_guide, f, indent=2)
            print(f"📋 Integration guide saved to: {guide_filename}")

def main():
    """Run the Survey API discovery"""
    
    discovery = ZohoSurveyDiscovery()
    
    # Run discovery
    report = discovery.run_survey_discovery()
    
    # Save results
    discovery.save_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SURVEY DISCOVERY SUMMARY")
    print("="*60)
    
    if report.get('error'):
        print(f"❌ Discovery failed: {report['error']}")
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Check if Survey API scope is included in OAuth token")
        print("   2. Required scopes: ZohoSurvey.surveys.READ, ZohoSurvey.responses.READ")
        print("   3. Survey API uses separate permissions from CRM API")
    else:
        print(f"✅ API Connection: {report['api_connection']}")
        print(f"✅ Course Surveys Found: {report['surveys_found']}")
        
        if report.get('recommendations'):
            print(f"\n🎯 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   • {rec}")

if __name__ == "__main__":
    main()