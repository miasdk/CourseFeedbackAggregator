#!/usr/bin/env python3
"""
Canvas Feedback Extractor
Extract and analyze actual feedback data from Executive Education courses
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import re
import time

load_dotenv()

class CanvasFeedbackExtractor:
    def __init__(self):
        self.access_token = os.getenv('CANVAS_ACCESS_TOKEN')
        self.api_url = os.getenv('CANVAS_API_URL', 'https://executiveeducation.instructure.com')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        self.results_dir = Path('feedback_extraction_results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Feedback detection keywords
        self.feedback_keywords = {
            'confusion': ['confusing', 'confused', 'unclear', 'don\'t understand', 'hard to follow'],
            'difficulty': ['difficult', 'hard', 'challenging', 'struggle', 'struggling'],
            'technical_issues': ['broken', 'not working', 'error', 'crash', 'can\'t access', 'cannot access'],
            'suggestions': ['suggest', 'recommend', 'should', 'could be better', 'improve'],
            'positive': ['great', 'excellent', 'helpful', 'clear', 'good', 'love', 'amazing'],
            'urgent': ['urgent', 'critical', 'immediately', 'asap', 'emergency']
        }
        
    def api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        url = f"{self.api_url}/api/v1/{endpoint}"
        try:
            # Rate limiting - Canvas allows 100 requests per 10 seconds
            time.sleep(0.1)
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                print(f"  ⚠️  Access denied to {endpoint}")
                return None
            elif response.status_code == 404:
                return []  # Empty result for missing resources
            else:
                print(f"  ⚠️  API Error {response.status_code}: {endpoint}")
                return None
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return None
    
    def categorize_feedback(self, text: str) -> Dict[str, Any]:
        """Categorize feedback text by type and urgency"""
        text_lower = text.lower()
        categories = []
        urgency_score = 0
        
        for category, keywords in self.feedback_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
                
                # Assign urgency scores
                if category == 'technical_issues':
                    urgency_score += 5
                elif category == 'urgent':
                    urgency_score += 10
                elif category == 'confusion':
                    urgency_score += 3
                elif category == 'difficulty':
                    urgency_score += 2
                elif category == 'suggestions':
                    urgency_score += 1
        
        return {
            'categories': categories,
            'urgency_score': urgency_score,
            'is_feedback': len(categories) > 0,
            'is_urgent': urgency_score >= 5
        }
    
    def extract_course_discussions(self, course_id: int, course_name: str) -> List[Dict]:
        """Extract all discussion posts and replies from a course"""
        print(f"  📝 Extracting discussions from: {course_name}")
        
        discussions = self.api_request(f'courses/{course_id}/discussion_topics')
        if not discussions:
            return []
        
        all_feedback = []
        print(f"    Found {len(discussions)} discussion topics")
        
        for topic in discussions[:10]:  # Limit to first 10 topics per course
            topic_id = topic.get('id')
            topic_title = topic.get('title', 'Untitled')
            
            # Get discussion entries
            entries = self.api_request(f'courses/{course_id}/discussion_topics/{topic_id}/entries')
            if not entries:
                continue
                
            print(f"      • {topic_title}: {len(entries)} entries")
            
            for entry in entries:
                message = entry.get('message', '')
                if not message:
                    continue
                    
                # Clean HTML tags from message
                clean_message = re.sub(r'<[^>]+>', '', message)
                
                # Skip very short messages
                if len(clean_message.strip()) < 20:
                    continue
                
                # Categorize the feedback
                feedback_analysis = self.categorize_feedback(clean_message)
                
                if feedback_analysis['is_feedback']:
                    feedback_entry = {
                        'course_id': course_id,
                        'course_name': course_name,
                        'source': 'discussion',
                        'topic_title': topic_title,
                        'message': clean_message[:500],  # Truncate for storage
                        'created_at': entry.get('created_at'),
                        'user_id': entry.get('user_id'),
                        'categories': feedback_analysis['categories'],
                        'urgency_score': feedback_analysis['urgency_score'],
                        'is_urgent': feedback_analysis['is_urgent']
                    }
                    all_feedback.append(feedback_entry)
        
        return all_feedback
    
    def extract_course_assignments(self, course_id: int, course_name: str) -> List[Dict]:
        """Extract assignment submission comments"""
        print(f"  📚 Extracting assignments from: {course_name}")
        
        assignments = self.api_request(f'courses/{course_id}/assignments')
        if not assignments:
            return []
        
        all_feedback = []
        print(f"    Found {len(assignments)} assignments")
        
        for assignment in assignments[:10]:  # Limit to first 10 assignments
            assignment_id = assignment.get('id')
            assignment_name = assignment.get('name', 'Untitled')
            
            # Get submissions with comments
            submissions = self.api_request(
                f'courses/{course_id}/assignments/{assignment_id}/submissions',
                params={'include[]': 'submission_comments'}
            )
            
            if not submissions:
                continue
            
            comment_count = 0
            for submission in submissions:
                for comment in submission.get('submission_comments', []):
                    comment_text = comment.get('comment', '')
                    if not comment_text or len(comment_text.strip()) < 20:
                        continue
                    
                    feedback_analysis = self.categorize_feedback(comment_text)
                    
                    if feedback_analysis['is_feedback']:
                        feedback_entry = {
                            'course_id': course_id,
                            'course_name': course_name,
                            'source': 'assignment_comment',
                            'assignment_name': assignment_name,
                            'message': comment_text[:500],
                            'created_at': comment.get('created_at'),
                            'author_id': comment.get('author_id'),
                            'categories': feedback_analysis['categories'],
                            'urgency_score': feedback_analysis['urgency_score'],
                            'is_urgent': feedback_analysis['is_urgent']
                        }
                        all_feedback.append(feedback_entry)
                        comment_count += 1
            
            if comment_count > 0:
                print(f"      • {assignment_name}: {comment_count} feedback comments")
        
        return all_feedback
    
    def extract_course_analytics(self, course_id: int, course_name: str) -> Dict[str, Any]:
        """Extract course analytics data"""
        analytics = {}
        
        # Try to get course activity data
        activity = self.api_request(f'courses/{course_id}/analytics/activity')
        if activity:
            analytics['activity'] = activity
        
        # Try to get student summaries
        student_summaries = self.api_request(f'courses/{course_id}/analytics/student_summaries')
        if student_summaries:
            analytics['student_summaries'] = student_summaries
            
            # Analyze engagement issues
            low_participation = [
                s for s in student_summaries 
                if s.get('participations', 0) < 5 or s.get('page_views', 0) < 50
            ]
            
            if low_participation:
                analytics['engagement_issues'] = {
                    'low_participation_count': len(low_participation),
                    'total_students': len(student_summaries),
                    'low_participation_rate': len(low_participation) / len(student_summaries)
                }
        
        return analytics
    
    def process_executive_courses(self, max_courses: int = 10) -> Dict[str, Any]:
        """Process Executive Education courses to extract feedback"""
        print("\n🎓 PROCESSING EXECUTIVE EDUCATION COURSES")
        print("="*60)
        
        # Load the course list from previous exploration
        account_results_file = 'account_exploration_results.json'
        if os.path.exists(account_results_file):
            with open(account_results_file, 'r') as f:
                account_data = json.load(f)
            courses = account_data.get('executive_education_courses', [])
        else:
            print("❌ No course data found. Run canvas_account_explorer.py first.")
            return {}
        
        print(f"Found {len(courses)} Executive Education courses")
        print(f"Will process up to {max_courses} courses for detailed feedback extraction")
        
        # Filter for active/available courses
        active_courses = [
            c for c in courses 
            if c.get('workflow_state') in ['available', 'completed']
        ][:max_courses]
        
        print(f"Processing {len(active_courses)} active courses...")
        
        all_feedback = []
        course_summaries = []
        
        for i, course in enumerate(active_courses):
            course_id = course.get('id')
            course_name = course.get('name', 'Unnamed Course')
            
            print(f"\n📋 [{i+1}/{len(active_courses)}] Processing: {course_name}")
            print(f"    Course ID: {course_id}, State: {course.get('workflow_state')}")
            
            course_feedback = []
            course_analytics = {}
            
            # Extract discussions
            discussion_feedback = self.extract_course_discussions(course_id, course_name)
            course_feedback.extend(discussion_feedback)
            
            # Extract assignment comments
            assignment_feedback = self.extract_course_assignments(course_id, course_name)
            course_feedback.extend(assignment_feedback)
            
            # Extract analytics
            course_analytics = self.extract_course_analytics(course_id, course_name)
            
            # Summarize course feedback
            urgent_feedback = [f for f in course_feedback if f['is_urgent']]
            
            course_summary = {
                'course_id': course_id,
                'course_name': course_name,
                'workflow_state': course.get('workflow_state'),
                'total_feedback_items': len(course_feedback),
                'urgent_issues': len(urgent_feedback),
                'feedback_categories': {},
                'analytics': course_analytics
            }
            
            # Count categories
            for feedback in course_feedback:
                for category in feedback['categories']:
                    course_summary['feedback_categories'][category] = \
                        course_summary['feedback_categories'].get(category, 0) + 1
            
            course_summaries.append(course_summary)
            all_feedback.extend(course_feedback)
            
            print(f"    → {len(course_feedback)} feedback items found ({len(urgent_feedback)} urgent)")
        
        # Create comprehensive analysis
        analysis_results = {
            'extraction_timestamp': datetime.now().isoformat(),
            'courses_processed': len(active_courses),
            'total_feedback_items': len(all_feedback),
            'urgent_issues_count': len([f for f in all_feedback if f['is_urgent']]),
            'course_summaries': course_summaries,
            'top_issues': self.analyze_top_issues(all_feedback),
            'feedback_trends': self.analyze_feedback_trends(all_feedback),
            'raw_feedback_sample': all_feedback[:50]  # Sample for review
        }
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = self.results_dir / f'executive_feedback_analysis_{timestamp}.json'
        
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n📊 EXTRACTION COMPLETE")
        print("="*60)
        print(f"✅ Processed: {len(active_courses)} courses")
        print(f"📝 Total feedback items: {len(all_feedback)}")
        print(f"⚠️  Urgent issues: {analysis_results['urgent_issues_count']}")
        print(f"💾 Results saved: {results_file}")
        
        return analysis_results
    
    def analyze_top_issues(self, feedback_items: List[Dict]) -> List[Dict]:
        """Analyze top issues across all feedback"""
        category_counts = {}
        
        for item in feedback_items:
            for category in item['categories']:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by frequency
        top_issues = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'category': category, 'count': count, 'percentage': round(count/len(feedback_items)*100, 1)}
            for category, count in top_issues
        ]
    
    def analyze_feedback_trends(self, feedback_items: List[Dict]) -> Dict[str, Any]:
        """Analyze feedback trends and patterns"""
        if not feedback_items:
            return {}
        
        # Source distribution
        source_counts = {}
        for item in feedback_items:
            source = item['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Urgency distribution
        urgency_scores = [item['urgency_score'] for item in feedback_items]
        avg_urgency = sum(urgency_scores) / len(urgency_scores)
        
        # Course distribution
        course_counts = {}
        for item in feedback_items:
            course = item['course_name']
            course_counts[course] = course_counts.get(course, 0) + 1
        
        top_courses_with_issues = sorted(
            course_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'source_distribution': source_counts,
            'average_urgency_score': round(avg_urgency, 2),
            'courses_with_most_feedback': top_courses_with_issues,
            'total_unique_courses': len(course_counts)
        }


if __name__ == "__main__":
    extractor = CanvasFeedbackExtractor()
    results = extractor.process_executive_courses(max_courses=15)  # Process 15 courses
    
    if results:
        print("\n🔍 KEY FINDINGS:")
        print(f"   • {results['courses_processed']} courses analyzed")
        print(f"   • {results['total_feedback_items']} feedback items extracted")
        print(f"   • {results['urgent_issues_count']} urgent issues identified")
        
        if results['top_issues']:
            print(f"\n📈 TOP ISSUE CATEGORIES:")
            for issue in results['top_issues'][:5]:
                print(f"   • {issue['category']}: {issue['count']} instances ({issue['percentage']}%)")
        
        if results['feedback_trends']['courses_with_most_feedback']:
            print(f"\n⚠️  COURSES WITH MOST FEEDBACK:")
            for course, count in results['feedback_trends']['courses_with_most_feedback'][:5]:
                print(f"   • {course}: {count} feedback items")