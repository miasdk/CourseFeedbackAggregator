/**
 * Webhook monitoring API service
 * Handles real-time webhook status and activity
 */

import apiClient from './client';

export interface WebhookEvent {
  id: string;
  source: 'zoho_survey' | 'canvas_lms';
  eventType: string;
  timestamp: string;
  payload: any;
  processed: boolean;
  processingTime?: number;
  error?: string;
  courseId?: string;
  courseName?: string;
}

export interface WebhookStats {
  total: number;
  processed: number;
  failed: number;
  avgProcessingTime: number;
  lastEvent?: string;
  sources: {
    zoho: { count: number; lastSeen: string };
    canvas: { count: number; lastSeen: string };
  };
}

export const webhookApi = {
  /**
   * Get recent webhook events
   */
  async getRecentEvents(params?: {
    limit?: number;
    source?: 'zoho_survey' | 'canvas_lms';
    processed?: boolean;
    startDate?: string;
  }) {
    const response = await apiClient.get<{
      events: WebhookEvent[];
      total: number;
    }>('/api/webhooks/recent', params);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get webhook statistics
   */
  async getWebhookStats(timeRange?: '1h' | '24h' | '7d' | '30d') {
    const response = await apiClient.get<WebhookStats>(
      '/api/webhooks/stats',
      timeRange ? { range: timeRange } : undefined
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get detailed webhook event
   */
  async getEventDetail(eventId: string) {
    const response = await apiClient.get<WebhookEvent>(
      `/api/webhooks/events/${eventId}`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Retry processing a failed webhook event
   */
  async retryEvent(eventId: string) {
    const response = await apiClient.post<{
      status: string;
      message: string;
    }>(`/api/webhooks/events/${eventId}/retry`);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get webhook health status
   */
  async getHealthStatus() {
    const response = await apiClient.get<{
      status: 'healthy' | 'degraded' | 'down';
      services: {
        zoho: {
          status: 'connected' | 'disconnected' | 'error';
          lastPing: string;
          message?: string;
        };
        canvas: {
          status: 'connected' | 'disconnected' | 'error';
          lastPing: string;
          message?: string;
        };
      };
      uptime: number;
    }>('/api/webhooks/health');

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Test webhook endpoint connectivity
   */
  async testWebhook(source: 'zoho' | 'canvas', testData?: any) {
    const response = await apiClient.post<{
      success: boolean;
      message: string;
      responseTime: number;
    }>(`/api/webhooks/test/${source}`, testData);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Subscribe to webhook events via SSE
   * Returns an EventSource for real-time updates
   */
  createEventStream(types?: string[]): EventSource {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const params = types ? `?types=${types.join(',')}` : '';
    const url = `${baseUrl}/api/webhooks/stream${params}`;

    return new EventSource(url);
  },
};