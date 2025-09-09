import { ScoringWeights, Recommendation, DataSourceStatus } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

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
    const response = await this.request<{
      priorities: Recommendation[];
      pagination: any;
      current_weights: any;
      filters_applied: any;
    }>('/api/priorities');
    return response.priorities;
  }

  async recomputePriorities(): Promise<{ message: string }> {
    return this.request('/api/priorities/recompute', { method: 'POST' });
  }

  async validateRecommendation(id: string, notes: string, validator: string): Promise<{ message: string }> {
    return this.request(`/api/priorities/${id}/validate`, {
      method: 'POST',
      body: JSON.stringify({ notes, validator })
    });
  }

  // Weight configuration endpoints
  async getWeights(): Promise<ScoringWeights> {
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
    return this.request('/api/weights', {
      method: 'PUT',
      body: JSON.stringify(weights)
    });
  }

  async resetWeights(): Promise<ScoringWeights> {
    return this.request<ScoringWeights>('/api/weights/reset', { method: 'POST' });
  }

  // Data ingestion endpoints
  async syncCanvas(): Promise<{ message: string; synced_items: number }> {
    return this.request('/api/ingest/canvas', { method: 'POST' });
  }

  async syncZoho(): Promise<{ message: string; synced_items: number }> {
    return this.request('/api/ingest/zoho', { method: 'POST' });
  }

  // Mock data source status (until backend implements this)
  async getDataSourceStatus(): Promise<DataSourceStatus> {
    return {
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
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }
}

export const apiClient = new ApiClient();