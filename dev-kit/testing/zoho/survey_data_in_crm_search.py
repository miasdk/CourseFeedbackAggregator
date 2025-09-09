#!/usr/bin/env python3
"""
Search for survey data within Zoho CRM modules
Since direct Survey API access is challenging, check if survey responses 
are integrated into CRM modules via Zoho's built-in integrations
"""

import os
import json
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

class SurveyDataInCRMSearch:
    """Search for survey response data within CRM modules"""
    
    def __init__(self):
        self.access_token = os.getenv('ZOHO_ACCESS_TOKEN')
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}'
        }
        self.api_domain = 'https://www.zohoapis.com'
        
        # Survey-related keywords to search for
        self.survey_keywords = [
            'survey', 'response', 'answer', 'questionnaire', 'poll',
            'evaluation', 'assessment', 'rating', 'score', 'review'
        ]
        
        # Course evaluation specific terms
        self.evaluation_terms = [
            'course evaluation', 'program feedback', 'training assessment',
            'instructor rating', 'content rating', 'satisfaction',
            'recommendation', 'improvement', 'quality'
        ]
    
    def search_records_for_surveys(self, module_name: str) -> Dict:
        """Search records in a module for survey-related content"""
        
        print(f"\n🔍 Searching {module_name} for survey data...")
        
        results = {
            'module': module_name,
            'survey_records': [],
            'total_matches': 0,
            'sample_data': {}
        }
        
        # Search for survey-related keywords
        for keyword in self.survey_keywords:
            try:
                response = requests.get(
                    f"{self.api_domain}/crm/v2/{module_name}/search",
                    headers=self.headers,
                    params={
                        'word': keyword,
                        'per_page': 20
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('data', [])
                    
                    if records:
                        print(f"   ✅ Found {len(records)} records containing '{keyword}'")
                        results['total_matches'] += len(records)
                        
                        # Analyze records for survey content
                        for record in records:
                            survey_fields = self.analyze_record_for_survey_data(record)
                            if survey_fields:
                                results['survey_records'].append({
                                    'record_id': record.get('id'),
                                    'survey_fields': survey_fields,
                                    'keyword_matched': keyword
                                })
                        
                        # Store sample record
                        if not results['sample_data'] and records:
                            results['sample_data'] = records[0]
                
                elif response.status_code == 204:
                    # No results for this keyword
                    pass
                else:
                    print(f"   ⚠️  Search error for '{keyword}': {response.status_code}")
            
            except Exception as e:
                print(f"   ❌ Error searching '{keyword}': {str(e)}")
        
        return results
    
    def analyze_record_for_survey_data(self, record: Dict) -> List[Dict]:
        """Analyze a single record for survey/evaluation content"""
        
        survey_fields = []
        
        for field_name, field_value in record.items():
            if field_name.startswith('$'):
                continue
            
            if not field_value:
                continue
            
            field_name_lower = field_name.lower()
            field_value_str = str(field_value).lower()
            
            # Check field name for survey indicators
            if any(term in field_name_lower for term in self.survey_keywords):
                survey_fields.append({
                    'field_name': field_name,
                    'field_value': str(field_value)[:200] if field_value else None,
                    'match_type': 'field_name',
                    'confidence': 'high'
                })
            
            # Check field content for evaluation terms
            elif any(term in field_value_str for term in self.evaluation_terms):
                survey_fields.append({
                    'field_name': field_name,
                    'field_value': str(field_value)[:200] if field_value else None,
                    'match_type': 'content',
                    'confidence': 'medium'
                })
            
            # Check for structured survey response patterns
            elif self.is_survey_response_pattern(field_value_str):
                survey_fields.append({
                    'field_name': field_name,
                    'field_value': str(field_value)[:200] if field_value else None,
                    'match_type': 'pattern',
                    'confidence': 'medium'
                })
        
        return survey_fields
    
    def is_survey_response_pattern(self, text: str) -> bool:
        """Check if text matches common survey response patterns"""
        
        if len(text) < 10:
            return False
        
        # Look for rating patterns (1-10, 1-5, etc.)
        rating_patterns = ['1-10', '1-5', 'strongly agree', 'strongly disagree', 'very satisfied']
        
        # Look for structured response patterns
        response_patterns = ['question:', 'answer:', 'q:', 'a:', 'response:', 'rating:']
        
        return any(pattern in text for pattern in rating_patterns + response_patterns)
    
    def search_custom_fields_for_surveys(self, module_name: str) -> Dict:
        """Get all custom fields and check for survey-related ones"""
        
        print(f"\n🔧 Checking custom fields in {module_name} for survey data...")
        
        try:
            # Get a sample record with all fields
            response = requests.get(
                f"{self.api_domain}/crm/v2/{module_name}",
                headers=self.headers,
                params={'per_page': 1}
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('data', [])
                
                if records:
                    record = records[0]
                    
                    # Find custom fields (usually have specific naming patterns)
                    custom_fields = []
                    survey_custom_fields = []
                    
                    for field_name, field_value in record.items():
                        if field_name.startswith('$'):
                            continue
                        
                        # Check if field might be custom (various indicators)
                        is_custom = (
                            '_' in field_name or  # Many custom fields use underscores
                            field_name.startswith('Custom_') or
                            field_name.startswith('CF_') or
                            any(word in field_name.lower() for word in self.survey_keywords)
                        )
                        
                        if is_custom:
                            custom_fields.append(field_name)
                            
                            # Check if custom field is survey-related
                            if any(term in field_name.lower() for term in self.survey_keywords):
                                survey_custom_fields.append({
                                    'field_name': field_name,
                                    'sample_value': str(field_value)[:100] if field_value else None,
                                    'data_type': type(field_value).__name__
                                })
                    
                    print(f"   ✅ Found {len(custom_fields)} custom fields")
                    if survey_custom_fields:
                        print(f"   📋 {len(survey_custom_fields)} survey-related custom fields:")
                        for field in survey_custom_fields:
                            print(f"      • {field['field_name']} ({field['data_type']})")
                    
                    return {
                        'module': module_name,
                        'total_custom_fields': len(custom_fields),
                        'survey_custom_fields': survey_custom_fields,
                        'all_custom_fields': custom_fields
                    }
            
            return {'module': module_name, 'error': f"Status {response.status_code}"}
        
        except Exception as e:
            return {'module': module_name, 'error': str(e)}
    
    def run_comprehensive_survey_search(self) -> Dict:
        """Run comprehensive search for survey data in CRM"""
        
        print("="*60)
        print("🔍 SEARCHING FOR SURVEY DATA IN ZOHO CRM")
        print("="*60)
        
        search_report = {
            'timestamp': datetime.now().isoformat(),
            'modules_searched': [],
            'survey_data_found': {},
            'custom_fields_analysis': {},
            'recommendations': []
        }
        
        modules_to_search = ['Contacts', 'Deals', 'Accounts', 'Leads']
        
        for module in modules_to_search:
            print(f"\n{'='*40}")
            print(f"SEARCHING MODULE: {module}")
            print('='*40)
            
            # Search for survey content in records
            survey_results = self.search_records_for_surveys(module)
            search_report['survey_data_found'][module] = survey_results
            
            # Analyze custom fields
            custom_fields_results = self.search_custom_fields_for_surveys(module)
            search_report['custom_fields_analysis'][module] = custom_fields_results
            
            search_report['modules_searched'].append(module)
        
        # Generate recommendations
        search_report['recommendations'] = self.generate_search_recommendations(search_report)
        
        return search_report
    
    def generate_search_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on survey data search"""
        
        recommendations = []
        
        # Check for direct survey matches
        total_survey_records = 0
        for module_data in report['survey_data_found'].values():
            total_survey_records += len(module_data.get('survey_records', []))
        
        if total_survey_records > 0:
            recommendations.append(f"Found {total_survey_records} records with survey-related content in CRM")
        
        # Check for survey custom fields
        total_survey_fields = 0
        modules_with_survey_fields = []
        
        for module, custom_data in report['custom_fields_analysis'].items():
            survey_fields = custom_data.get('survey_custom_fields', [])
            if survey_fields:
                total_survey_fields += len(survey_fields)
                modules_with_survey_fields.append(module)
        
        if total_survey_fields > 0:
            recommendations.append(f"Found {total_survey_fields} survey-related custom fields")
            recommendations.append(f"Modules with survey fields: {', '.join(modules_with_survey_fields)}")
        
        # Strategic recommendations
        if total_survey_records > 0 or total_survey_fields > 0:
            recommendations.append("Survey data appears to be integrated into CRM - use CRM API for survey access")
        else:
            recommendations.append("No survey data found in CRM - may need direct Survey API access or data export")
        
        return recommendations
    
    def save_results(self, report: Dict):
        """Save search results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"survey_in_crm_search_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Survey search results saved to: {filename}")

def main():
    """Run the survey data search in CRM"""
    
    searcher = SurveyDataInCRMSearch()
    
    # Run comprehensive search
    report = searcher.run_comprehensive_survey_search()
    
    # Save results
    searcher.save_results(report)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SURVEY SEARCH SUMMARY")
    print("="*60)
    
    total_matches = sum(
        data.get('total_matches', 0) 
        for data in report['survey_data_found'].values()
    )
    
    total_survey_fields = sum(
        len(data.get('survey_custom_fields', [])) 
        for data in report['custom_fields_analysis'].values()
    )
    
    print(f"✅ Modules searched: {len(report['modules_searched'])}")
    print(f"✅ Records with survey keywords: {total_matches}")
    print(f"✅ Survey-related custom fields: {total_survey_fields}")
    
    if report['recommendations']:
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

if __name__ == "__main__":
    main()