#!/usr/bin/env python3
"""
Canvas Account Explorer
Explore Canvas accounts and find Executive Education courses
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class CanvasAccountExplorer:
    def __init__(self):
        self.access_token = os.getenv('CANVAS_ACCESS_TOKEN')
        self.api_url = os.getenv('CANVAS_API_URL', 'https://executiveeducation.instructure.com')
        self.account_id = os.getenv('CANVAS_ACCOUNT_ID')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
    def api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.api_url}/api/v1/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            print(f"  API Call: {endpoint} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response length: {len(data) if isinstance(data, list) else 'Object'}")
                return data
            else:
                print(f"  ⚠️  Error: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return None
    
    def explore_accounts(self):
        """Explore available accounts"""
        print("\n📋 EXPLORING ACCOUNTS")
        print("="*50)
        
        accounts = self.api_request('accounts')
        if accounts:
            print(f"Found {len(accounts)} accounts:")
            for account in accounts:
                print(f"  - {account.get('name', 'Unnamed')} (ID: {account.get('id')})")
                
                # Try to get courses from each account
                print(f"    Checking courses in account {account.get('id')}...")
                account_courses = self.api_request(
                    f"accounts/{account.get('id')}/courses",
                    params={'per_page': 100, 'include[]': ['teachers', 'total_students']}
                )
                
                if account_courses:
                    print(f"    → Found {len(account_courses)} courses in this account")
                    for course in account_courses[:5]:  # Show first 5
                        print(f"      • {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
                        print(f"        State: {course.get('workflow_state')}, Students: {course.get('total_students', 'N/A')}")
                else:
                    print("    → No courses found or access denied")
        
        return accounts
    
    def explore_specific_account(self, account_id: str):
        """Explore a specific account in detail"""
        print(f"\n🏢 EXPLORING ACCOUNT: {account_id}")
        print("="*50)
        
        # Get account info
        account_info = self.api_request(f'accounts/{account_id}')
        if account_info:
            print(f"Account Name: {account_info.get('name')}")
            print(f"Domain: {account_info.get('domain')}")
        
        # Get sub-accounts
        print("\n📂 Sub-accounts:")
        sub_accounts = self.api_request(f'accounts/{account_id}/sub_accounts')
        if sub_accounts:
            for sub in sub_accounts:
                print(f"  - {sub.get('name')} (ID: {sub.get('id')})")
                
                # Check courses in sub-account
                sub_courses = self.api_request(
                    f"accounts/{sub.get('id')}/courses",
                    params={'per_page': 100}
                )
                if sub_courses:
                    print(f"    → {len(sub_courses)} courses")
        
        # Get courses from main account with different parameters
        print(f"\n📚 Courses in account {account_id}:")
        
        course_params = [
            {'state[]': ['available'], 'per_page': 100},
            {'state[]': ['completed'], 'per_page': 100},
            {'enrollment_state': 'active', 'per_page': 100},
            {'per_page': 100}  # All courses
        ]
        
        all_courses = []
        for i, params in enumerate(course_params):
            print(f"  Attempt {i+1}: {params}")
            courses = self.api_request(f"accounts/{account_id}/courses", params)
            if courses:
                print(f"    → Found {len(courses)} courses")
                all_courses.extend(courses)
                
                # Show sample courses
                for course in courses[:3]:
                    print(f"      • {course.get('name', 'Unnamed')}")
                    print(f"        ID: {course.get('id')}, State: {course.get('workflow_state')}")
                    print(f"        Created: {course.get('created_at', 'N/A')}")
        
        # Remove duplicates
        unique_courses = {c['id']: c for c in all_courses}.values()
        return list(unique_courses)
    
    def search_executive_education(self):
        """Search for Executive Education related content"""
        print("\n🎓 SEARCHING FOR EXECUTIVE EDUCATION")
        print("="*50)
        
        # Search terms related to executive education
        search_terms = [
            'executive',
            'education', 
            'professional',
            'certificate',
            'leadership',
            'management'
        ]
        
        all_results = []
        
        # Try different account contexts
        account_ids_to_try = []
        if self.account_id:
            account_ids_to_try.append(self.account_id)
        
        # Also try root accounts
        accounts = self.api_request('accounts')
        if accounts:
            for account in accounts:
                account_ids_to_try.append(str(account.get('id')))
        
        for account_id in account_ids_to_try:
            print(f"\n  Searching in account {account_id}:")
            
            courses = self.api_request(
                f"accounts/{account_id}/courses",
                params={'per_page': 100, 'search_term': 'executive'}
            )
            
            if courses:
                print(f"    Found {len(courses)} courses with 'executive' search")
                all_results.extend(courses)
            
            # Try broader search
            all_courses = self.api_request(
                f"accounts/{account_id}/courses",
                params={'per_page': 100}
            )
            
            if all_courses:
                # Filter by name containing executive education terms
                filtered = []
                for course in all_courses:
                    name = course.get('name', '').lower()
                    if any(term in name for term in search_terms):
                        filtered.append(course)
                
                if filtered:
                    print(f"    Found {len(filtered)} courses matching executive education terms")
                    all_results.extend(filtered)
        
        # Remove duplicates and show results
        unique_results = {c['id']: c for c in all_results}.values()
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total unique courses found: {len(unique_results)}")
        
        for course in unique_results:
            print(f"  • {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
            print(f"    State: {course.get('workflow_state')}")
            print(f"    Students: {course.get('total_students', 'N/A')}")
        
        return list(unique_results)
    
    def run_account_exploration(self):
        """Run complete account exploration"""
        print("="*60)
        print("CANVAS ACCOUNT EXPLORATION")
        print("="*60)
        
        # Test connection first
        user_data = self.api_request('users/self')
        if not user_data:
            print("❌ Cannot connect to Canvas API")
            return
        
        print(f"✅ Connected as: {user_data.get('name')}")
        
        # Explore all accessible accounts
        accounts = self.explore_accounts()
        
        # Explore specific account if provided
        if self.account_id:
            courses = self.explore_specific_account(self.account_id)
            print(f"\n📊 Found {len(courses)} total courses in account {self.account_id}")
        
        # Search for executive education content
        executive_courses = self.search_executive_education()
        
        # Save results
        results = {
            'exploration_timestamp': datetime.now().isoformat(),
            'user_info': user_data,
            'accounts_found': accounts or [],
            'executive_education_courses': executive_courses or [],
            'total_executive_courses': len(executive_courses) if executive_courses else 0
        }
        
        with open('account_exploration_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: account_exploration_results.json")
        return results


if __name__ == "__main__":
    explorer = CanvasAccountExplorer()
    explorer.run_account_exploration()