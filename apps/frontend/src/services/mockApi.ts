import { ScoringWeights, Recommendation, DataSourceStatus } from '../types';

// Mock data for demo purposes
const MOCK_RECOMMENDATIONS: Recommendation[] = [
  {
    id: 'rec-001',
    course_id: 'course-it-leadership',
    course_name: 'IT Leadership',
    title: 'Video Inconsistency in Module 1',
    description: 'Video 1 and Video 2 talk about different attributes - this offers inconsistency that confuses students about core leadership principles',
    category: 'content',
    priority_score: 8.7,
    impact_score: 9.2,
    urgency_score: 8.5,
    effort_score: 6.0,
    strategic_score: 8.8,
    trend_score: 7.5,
    affected_students: 23,
    feedback_count: 8,
    is_show_stopper: false,
    created_at: '2024-09-05T10:30:00Z',
    status: 'pending'
  },
  {
    id: 'rec-002',
    course_id: 'course-customer-exp',
    course_name: 'Customer Experience Program',
    title: 'Navigation Issues in Assessment Section',
    description: 'Students cannot find the final assessment link, causing completion delays and frustration',
    category: 'navigation',
    priority_score: 7.8,
    impact_score: 8.5,
    urgency_score: 9.0,
    effort_score: 4.5,
    strategic_score: 6.5,
    trend_score: 8.0,
    affected_students: 45,
    feedback_count: 12,
    is_show_stopper: true,
    created_at: '2024-09-04T14:15:00Z',
    status: 'pending'
  },
  {
    id: 'rec-003',
    course_id: 'course-data-analytics',
    course_name: 'Data Analytics Fundamentals',
    title: 'Outdated Excel Examples',
    description: 'Examples use Excel 2016 interface which differs from current Office 365, causing confusion',
    category: 'content',
    priority_score: 6.2,
    impact_score: 7.0,
    urgency_score: 5.5,
    effort_score: 7.0,
    strategic_score: 6.0,
    trend_score: 6.5,
    affected_students: 31,
    feedback_count: 6,
    is_show_stopper: false,
    created_at: '2024-09-03T09:45:00Z',
    status: 'validated',
    validator: 'Sarah Chen',
    validation_notes: 'Confirmed - will update in next content cycle'
  },
  {
    id: 'rec-004',
    course_id: 'course-project-mgmt',
    course_name: 'Project Management Essentials',
    title: 'Quiz Timer Issues',
    description: 'Timer countdown not working properly on mobile devices, students lose progress',
    category: 'technical',
    priority_score: 8.1,
    impact_score: 8.8,
    urgency_score: 8.5,
    effort_score: 5.5,
    strategic_score: 7.0,
    trend_score: 9.0,
    affected_students: 67,
    feedback_count: 15,
    is_show_stopper: true,
    created_at: '2024-09-02T16:20:00Z',
    status: 'in_progress'
  },
  {
    id: 'rec-005',
    course_id: 'course-digital-marketing',
    course_name: 'Digital Marketing Strategy',
    title: 'Missing Video Transcripts',
    description: 'Accessibility issue - video content lacks proper transcripts for hearing impaired students',
    category: 'content',
    priority_score: 4.8,
    impact_score: 6.0,
    urgency_score: 4.5,
    effort_score: 3.5,
    strategic_score: 8.5,
    trend_score: 5.0,
    affected_students: 12,
    feedback_count: 4,
    is_show_stopper: false,
    created_at: '2024-09-01T11:10:00Z',
    status: 'pending'
  }
];

const MOCK_WEIGHTS: ScoringWeights = {
  impact: 0.25,
  urgency: 0.25,
  effort: 0.20,
  strategic: 0.20,
  trend: 0.10
};

const MOCK_DATA_SOURCE_STATUS: DataSourceStatus = {
  canvas: {
    connected: true,
    last_sync: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
    courses_synced: 12,
    feedback_items: 156
  },
  zoho: {
    connected: true,
    last_sync: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
    surveys_synced: 8,
    responses: 689
  }
};

export class MockApiClient {
  private delay(ms: number = 500): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Priority/Recommendations endpoints
  async getPriorities(): Promise<Recommendation[]> {
    await this.delay();
    return MOCK_RECOMMENDATIONS;
  }

  async recomputePriorities(): Promise<{ message: string }> {
    await this.delay(1000);
    return { message: 'Priorities recomputed successfully with updated scoring weights' };
  }

  async validateRecommendation(id: string, notes: string, validator: string): Promise<{ message: string }> {
    await this.delay();
    
    // Update the mock data
    const recommendation = MOCK_RECOMMENDATIONS.find(r => r.id === id);
    if (recommendation) {
      recommendation.status = 'validated';
      recommendation.validator = validator;
      recommendation.validation_notes = notes;
    }
    
    return { message: `Recommendation ${id} validated successfully` };
  }

  // Weight configuration endpoints
  async getWeights(): Promise<ScoringWeights> {
    await this.delay();
    return { ...MOCK_WEIGHTS };
  }

  async updateWeights(weights: ScoringWeights): Promise<{ message: string }> {
    await this.delay();
    
    // Update mock weights
    Object.assign(MOCK_WEIGHTS, weights);
    
    return { message: 'Scoring weights updated successfully' };
  }

  async resetWeights(): Promise<ScoringWeights> {
    await this.delay();
    
    // Reset to default weights
    const defaultWeights: ScoringWeights = {
      impact: 0.25,
      urgency: 0.25,
      effort: 0.20,
      strategic: 0.20,
      trend: 0.10
    };
    
    Object.assign(MOCK_WEIGHTS, defaultWeights);
    return { ...defaultWeights };
  }

  // Data ingestion endpoints
  async syncCanvas(): Promise<{ message: string; synced_items: number }> {
    await this.delay(2000);
    
    // Update last sync time
    MOCK_DATA_SOURCE_STATUS.canvas.last_sync = new Date().toISOString();
    MOCK_DATA_SOURCE_STATUS.canvas.feedback_items += Math.floor(Math.random() * 10) + 1;
    
    return { 
      message: 'Canvas data synchronized successfully', 
      synced_items: Math.floor(Math.random() * 15) + 5 
    };
  }

  async syncZoho(): Promise<{ message: string; synced_items: number }> {
    await this.delay(2000);
    
    // Update last sync time
    MOCK_DATA_SOURCE_STATUS.zoho.last_sync = new Date().toISOString();
    MOCK_DATA_SOURCE_STATUS.zoho.responses += Math.floor(Math.random() * 20) + 5;
    
    return { 
      message: 'Zoho survey data synchronized successfully', 
      synced_items: Math.floor(Math.random() * 25) + 10 
    };
  }

  // Data source status
  async getDataSourceStatus(): Promise<DataSourceStatus> {
    await this.delay();
    return { ...MOCK_DATA_SOURCE_STATUS };
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    await this.delay();
    return { 
      status: 'ok (mock mode)', 
      timestamp: new Date().toISOString() 
    };
  }
}

export const mockApiClient = new MockApiClient();