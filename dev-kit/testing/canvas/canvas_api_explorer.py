#!/usr/bin/env python3
"""
Canvas LMS API Explorer
Comprehensive testing script to explore Canvas API data structures
and identify available course feedback data.
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CanvasAPIExplorer:
    def __init__(self):
        self.access_token = os.getenv('CANVAS_ACCESS_TOKEN')
        self.api_url = os.getenv('CANVAS_API_URL', 'https://executiveeducation.instructure.com')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        self.results_dir = Path('canvas_exploration_results')
        self.results_dir.mkdir(exist_ok=True)
        
    def save_results(self, data: Any, filename: str):
        """Save results to JSON file for analysis"""
        filepath = self.results_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  → Saved to {filepath}")
        return filepath
    
    def api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.api_url}/api/v1/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            print(f"  API Call: {endpoint} - Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ⚠️  Error: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return None
    
    def test_connection(self):
        """Test basic API connection"""
        print("\n1️⃣  TESTING CONNECTION")
        print("="*50)
        
        user_data = self.api_request('users/self')
        if user_data:
            print(f"  ✅ Connected as: {user_data.get('name', 'Unknown')}")
            print(f"  Email: {user_data.get('email', 'N/A')}")
            print(f"  User ID: {user_data.get('id', 'N/A')}")
            self.save_results(user_data, 'user_profile')
            return True
        else:
            print("  ❌ Connection failed!")
            return False
    
    def explore_courses(self):
        """Explore available courses"""
        print("\n2️⃣  EXPLORING COURSES")
        print("="*50)
        
        # Try different approaches to get courses
        approaches = [
            {
                'name': 'Active Enrollments',
                'params': {
                    'enrollment_state': 'active',
                    'include[]': ['teachers', 'total_students', 'term'],
                    'per_page': 100
                }
            },
            {
                'name': 'All Enrollment Types',
                'params': {
                    'enrollment_type[]': ['teacher', 'ta', 'student', 'observer'],
                    'per_page': 100
                }
            },
            {
                'name': 'Published Courses',
                'params': {
                    'state[]': ['available'],
                    'per_page': 100
                }
            }
        ]
        
        all_courses = []
        for approach in approaches:
            print(f"\n  Trying: {approach['name']}")
            courses = self.api_request('courses', approach['params'])
            if courses:
                print(f"  Found {len(courses)} courses")
                all_courses.extend(courses)
                
                # Display sample course info
                for i, course in enumerate(courses[:3]):
                    print(f"    - {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
                    print(f"      Students: {course.get('total_students', 'N/A')}")
                    print(f"      State: {course.get('workflow_state', 'N/A')}")
        
        # Save unique courses
        unique_courses = {c['id']: c for c in all_courses}.values()
        self.save_results(list(unique_courses), 'courses_master_list')
        return list(unique_courses)
    
    def explore_course_content(self, course_id: int, course_name: str):
        """Deep dive into a specific course"""
        print(f"\n3️⃣  EXPLORING COURSE: {course_name} (ID: {course_id})")
        print("="*50)
        
        course_data = {
            'course_id': course_id,
            'course_name': course_name,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Get discussion topics
        print("\n  📝 Discussion Topics:")
        discussions = self.api_request(f'courses/{course_id}/discussion_topics')
        if discussions:
            print(f"    Found {len(discussions)} discussion topics")
            course_data['discussions'] = []
            
            for disc in discussions[:5]:  # Sample first 5
                print(f"    - {disc.get('title', 'Untitled')}")
                
                # Get entries for each discussion
                entries = self.api_request(f'courses/{course_id}/discussion_topics/{disc["id"]}/entries')
                if entries:
                    disc['entries'] = entries
                    print(f"      → {len(entries)} entries/responses")
                    
                    # Look for feedback keywords
                    feedback_entries = []
                    keywords = ['confusing', 'unclear', 'difficult', 'problem', 'issue', 
                               'suggest', 'improve', 'broken', 'error', 'help']
                    
                    for entry in entries:
                        message = entry.get('message', '').lower()
                        if any(keyword in message for keyword in keywords):
                            feedback_entries.append(entry)
                    
                    if feedback_entries:
                        print(f"      ⚠️  {len(feedback_entries)} entries contain feedback keywords")
                        disc['feedback_entries'] = feedback_entries
                
                course_data['discussions'].append(disc)
        
        # Get assignments
        print("\n  📚 Assignments:")
        assignments = self.api_request(f'courses/{course_id}/assignments')
        if assignments:
            print(f"    Found {len(assignments)} assignments")
            course_data['assignments'] = []
            
            for assign in assignments[:5]:  # Sample first 5
                print(f"    - {assign.get('name', 'Untitled')}")
                
                # Get submissions with comments
                submissions = self.api_request(
                    f'courses/{course_id}/assignments/{assign["id"]}/submissions',
                    params={'include[]': 'submission_comments'}
                )
                if submissions:
                    comments_count = sum(len(s.get('submission_comments', [])) for s in submissions)
                    print(f"      → {len(submissions)} submissions, {comments_count} comments")
                    assign['submissions_summary'] = {
                        'total_submissions': len(submissions),
                        'total_comments': comments_count,
                        'sample_comments': []
                    }
                    
                    # Extract sample comments
                    for sub in submissions:
                        for comment in sub.get('submission_comments', []):
                            assign['submissions_summary']['sample_comments'].append({
                                'comment': comment.get('comment', ''),
                                'created_at': comment.get('created_at', '')
                            })
                            if len(assign['submissions_summary']['sample_comments']) >= 5:
                                break
                
                course_data['assignments'].append(assign)
        
        # Get quizzes
        print("\n  ❓ Quizzes:")
        quizzes = self.api_request(f'courses/{course_id}/quizzes')
        if quizzes:
            print(f"    Found {len(quizzes)} quizzes")
            course_data['quizzes'] = quizzes[:5]  # Sample first 5
            
            for quiz in course_data['quizzes']:
                print(f"    - {quiz.get('title', 'Untitled')}")
                
                # Try to get statistics
                stats = self.api_request(f'courses/{course_id}/quizzes/{quiz["id"]}/statistics')
                if stats:
                    quiz['statistics'] = stats
                    print(f"      → Statistics available")
        
        # Get course analytics (if available)
        print("\n  📊 Course Analytics:")
        activity = self.api_request(f'courses/{course_id}/analytics/activity')
        if activity:
            print(f"    Activity data available")
            course_data['analytics_activity'] = activity
        
        student_summaries = self.api_request(f'courses/{course_id}/analytics/student_summaries')
        if student_summaries:
            print(f"    Found {len(student_summaries)} student summaries")
            course_data['student_summaries'] = student_summaries[:10]  # Sample first 10
        
        # Get modules
        print("\n  📦 Modules:")
        modules = self.api_request(f'courses/{course_id}/modules')
        if modules:
            print(f"    Found {len(modules)} modules")
            course_data['modules'] = []
            
            for module in modules[:5]:  # Sample first 5
                print(f"    - {module.get('name', 'Untitled')}")
                course_data['modules'].append({
                    'id': module.get('id'),
                    'name': module.get('name'),
                    'position': module.get('position'),
                    'items_count': module.get('items_count')
                })
        
        # Save course exploration results
        filename = f"course_deep_dive_{course_id}"
        self.save_results(course_data, filename)
        return course_data
    
    def analyze_feedback_patterns(self, courses_data: List[Dict]):
        """Analyze feedback patterns across courses"""
        print("\n4️⃣  ANALYZING FEEDBACK PATTERNS")
        print("="*50)
        
        feedback_analysis = {
            'total_courses_analyzed': len(courses_data),
            'feedback_keywords': {
                'confusing': 0,
                'unclear': 0,
                'difficult': 0,
                'problem': 0,
                'issue': 0,
                'broken': 0,
                'error': 0,
                'help': 0,
                'suggest': 0,
                'improve': 0
            },
            'urgent_issues': [],
            'common_themes': [],
            'courses_with_issues': []
        }
        
        for course in courses_data:
            course_issues = []
            
            # Analyze discussions
            for disc in course.get('discussions', []):
                for entry in disc.get('feedback_entries', []):
                    message = entry.get('message', '').lower()
                    for keyword in feedback_analysis['feedback_keywords']:
                        if keyword in message:
                            feedback_analysis['feedback_keywords'][keyword] += 1
                    
                    # Check for urgent issues
                    urgent_keywords = ['broken', 'error', 'cannot access', "can't", 'crash']
                    if any(kw in message for kw in urgent_keywords):
                        feedback_analysis['urgent_issues'].append({
                            'course': course.get('course_name'),
                            'source': 'discussion',
                            'message': entry.get('message', '')[:200],
                            'created_at': entry.get('created_at')
                        })
                        course_issues.append('urgent_technical_issue')
            
            # Analyze assignment comments
            for assign in course.get('assignments', []):
                for comment in assign.get('submissions_summary', {}).get('sample_comments', []):
                    comment_text = comment.get('comment', '').lower()
                    for keyword in feedback_analysis['feedback_keywords']:
                        if keyword in comment_text:
                            feedback_analysis['feedback_keywords'][keyword] += 1
            
            if course_issues:
                feedback_analysis['courses_with_issues'].append({
                    'course_name': course.get('course_name'),
                    'course_id': course.get('course_id'),
                    'issue_types': list(set(course_issues))
                })
        
        # Identify common themes
        top_keywords = sorted(
            feedback_analysis['feedback_keywords'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        feedback_analysis['common_themes'] = [
            {'keyword': kw, 'count': count} for kw, count in top_keywords
        ]
        
        print("\n  📊 Feedback Summary:")
        print(f"    Courses analyzed: {feedback_analysis['total_courses_analyzed']}")
        print(f"    Urgent issues found: {len(feedback_analysis['urgent_issues'])}")
        print(f"    Courses with issues: {len(feedback_analysis['courses_with_issues'])}")
        
        print("\n  🔝 Top Feedback Keywords:")
        for theme in feedback_analysis['common_themes']:
            print(f"    - '{theme['keyword']}': {theme['count']} occurrences")
        
        self.save_results(feedback_analysis, 'feedback_analysis')
        return feedback_analysis
    
    def run_comprehensive_exploration(self):
        """Run complete Canvas API exploration"""
        print("\n" + "="*60)
        print("CANVAS API COMPREHENSIVE EXPLORATION")
        print("="*60)
        
        # Test connection
        if not self.test_connection():
            return
        
        # Explore courses
        courses = self.explore_courses()
        if not courses:
            print("\n⚠️  No courses found. Check permissions or enrollment.")
            return
        
        # Deep dive into sample courses
        print(f"\n📚 Found {len(courses)} total courses")
        courses_to_explore = min(3, len(courses))  # Explore up to 3 courses
        print(f"   Will deep-dive into {courses_to_explore} courses for detailed analysis")
        
        detailed_course_data = []
        for course in courses[:courses_to_explore]:
            course_data = self.explore_course_content(
                course['id'],
                course.get('name', 'Unnamed Course')
            )
            detailed_course_data.append(course_data)
        
        # Analyze feedback patterns
        if detailed_course_data:
            self.analyze_feedback_patterns(detailed_course_data)
        
        # Create summary report
        summary = {
            'exploration_date': datetime.now().isoformat(),
            'connection_successful': True,
            'total_courses_found': len(courses),
            'courses_explored_in_detail': courses_to_explore,
            'data_types_available': [],
            'api_endpoints_tested': [
                'users/self',
                'courses',
                'discussion_topics',
                'assignments',
                'quizzes',
                'analytics'
            ]
        }
        
        # Check what data types are available
        if detailed_course_data:
            sample_course = detailed_course_data[0]
            if sample_course.get('discussions'):
                summary['data_types_available'].append('discussions')
            if sample_course.get('assignments'):
                summary['data_types_available'].append('assignments')
            if sample_course.get('quizzes'):
                summary['data_types_available'].append('quizzes')
            if sample_course.get('analytics_activity'):
                summary['data_types_available'].append('analytics')
            if sample_course.get('modules'):
                summary['data_types_available'].append('modules')
        
        print("\n" + "="*60)
        print("EXPLORATION COMPLETE")
        print("="*60)
        print(f"\n✅ Summary:")
        print(f"  - Courses found: {summary['total_courses_found']}")
        print(f"  - Courses analyzed: {summary['courses_explored_in_detail']}")
        print(f"  - Data types available: {', '.join(summary['data_types_available'])}")
        print(f"\n📁 Results saved in: {self.results_dir}/")
        
        self.save_results(summary, 'exploration_summary')
        return summary


if __name__ == "__main__":
    explorer = CanvasAPIExplorer()
    explorer.run_comprehensive_exploration()