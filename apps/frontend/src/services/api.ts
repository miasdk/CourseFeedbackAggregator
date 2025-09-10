import { ScoringWeights, Recommendation, DataSourceStatus } from '../types';
import { mockApiClient } from './mockApi';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';
const USE_MOCK_DATA = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true' || import.meta.env.NODE_ENV === 'development';

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

  // Priority/Recommendations endpoints
  async getPriorities(): Promise<Recommendation[]> {
    if (USE_MOCK_DATA) {
      console.log('🎭 Using mock data for priorities');
      return mockApiClient.getPriorities();
    }
    
    const response = await this.request<{
      priorities: Recommendation[];
      pagination: any;
      current_weights: any;
      filters_applied: any;
    }>('/api/priorities');
    return response.priorities;
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
    
    return this.request('/api/data-sources/status');
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