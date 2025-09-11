import { ScoringWeights, Recommendation, DataSourceStatus } from '../types';
import { mockApiClient } from './mockApi';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK_DATA = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Courses endpoints
  async getCourses(): Promise<any[]> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for courses');
      return mockApiClient.getCourses();
    }
    
    const response = await this.request<{
      success: boolean;
      count: number;
      courses: any[];
    }>('/api/courses');
    
    return response.courses;
  }

  // Priority/Recommendations endpoints
  async getPriorities(): Promise<Recommendation[]> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for priorities');
      return mockApiClient.getPriorities();
    }
    
    const response = await this.request<{
      priorities: any[];
      pagination: any;
      current_weights: any;
      filters_applied: any;
    }>('/api/priorities');
    
    // Transform backend data structure to match frontend expectations
    return response.priorities.map(priority => ({
      id: priority.id?.toString() || '',
      course_id: priority.course_id || '',
      course_name: this.extractCourseName(priority.course_id) || 'Unknown Course',
      title: priority.issue_summary || 'No title',
      description: priority.evidence?.[0]?.quote || 'No description available',
      category: this.categorizeIssue(priority.issue_summary || '') as 'content' | 'technical' | 'navigation' | 'assessment' | 'other',
      priority_score: priority.priority_score || 0,
      impact_score: priority.factor_scores?.impact || 0,
      urgency_score: priority.factor_scores?.urgency || 0,
      effort_score: priority.factor_scores?.effort || 0,
      strategic_score: priority.factor_scores?.strategic || 0,
      trend_score: priority.factor_scores?.trend || 0,
      affected_students: priority.students_affected || 0,
      feedback_count: priority.feedback_ids?.length || 0,
      is_show_stopper: priority.priority_score >= 5,
      created_at: priority.created_at || new Date().toISOString(),
      status: 'pending' as const,
      validator: undefined,
      validation_notes: undefined
    }));
  }

  private extractCourseName(courseId: string): string {
    // Extract readable course name from course_id
    if (courseId.includes('canvas')) {
      return `Canvas Course (${courseId.replace('canvas_', '')})`;
    }
    if (courseId.includes('zoho')) {
      return `Zoho Program (${courseId.replace('zoho_', '')})`;
    }
    return courseId;
  }

  private categorizeIssue(summary: string): 'content' | 'technical' | 'navigation' | 'assessment' | 'other' {
    const lowerSummary = summary.toLowerCase();
    if (lowerSummary.includes('video') || lowerSummary.includes('content')) return 'content';
    if (lowerSummary.includes('technical') || lowerSummary.includes('platform')) return 'technical';
    if (lowerSummary.includes('navigation') || lowerSummary.includes('menu')) return 'navigation';
    if (lowerSummary.includes('assignment') || lowerSummary.includes('assessment')) return 'assessment';
    return 'other';
  }

  async recomputePriorities(): Promise<{ message: string }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for recompute priorities');
      return mockApiClient.recomputePriorities();
    }
    
    return this.request('/api/priorities/recompute', { method: 'POST' });
  }

  async validateRecommendation(id: string, notes: string, validator: string): Promise<{ message: string }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for validate recommendation');
      return mockApiClient.validateRecommendation(id, notes, validator);
    }
    
    return this.request(`/api/priorities/${id}/validate`, {
      method: 'POST',
      body: JSON.stringify({ notes, validator })
    });
  }

  // Weight configuration endpoints
  async getWeights(): Promise<ScoringWeights> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for weights');
      return mockApiClient.getWeights();
    }
    
    const response = await this.request<{
      weights: ScoringWeights;
      weight_details: any;
      updated_at: string;
      updated_by: string;
      total: number;
    }>('/api/weights');
    return response.weights;
  }

  async updateWeights(weights: ScoringWeights): Promise<{ message: string }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for update weights');
      return mockApiClient.updateWeights(weights);
    }
    
    return this.request('/api/weights', {
      method: 'PUT',
      body: JSON.stringify(weights)
    });
  }

  async resetWeights(): Promise<ScoringWeights> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for reset weights');
      return mockApiClient.resetWeights();
    }
    
    return this.request<ScoringWeights>('/api/weights/reset', { method: 'POST' });
  }

  // Data ingestion endpoints
  async syncCanvas(): Promise<{ message: string; synced_items: number }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for Canvas sync');
      return mockApiClient.syncCanvas();
    }
    
    return this.request('/api/ingest/canvas', { method: 'POST' });
  }

  async syncZoho(): Promise<{ message: string; synced_items: number }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for Zoho sync');
      return mockApiClient.syncZoho();
    }
    
    return this.request('/api/ingest/zoho', { method: 'POST' });
  }

  async getDataSourceStatus(): Promise<DataSourceStatus> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for data source status');
      return mockApiClient.getDataSourceStatus();
    }
    
    const response = await this.request<any>('/api/data-sources/status');
    
    // Transform backend data structure to match frontend expectations
    return {
      canvas: {
        connected: response.canvas?.status === 'connected',
        last_sync: response.canvas?.last_sync || '',
        courses_synced: response.canvas?.courses_synced || 0,
        feedback_items: response.canvas?.feedback_count || 0
      },
      zoho: {
        connected: response.zoho?.status === 'connected',
        last_sync: response.zoho?.last_sync || '',
        surveys_synced: response.zoho?.programs_synced || 0,
        responses: response.zoho?.feedback_count || 0
      }
    };
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for health check');
      return mockApiClient.healthCheck();
    }
    
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();