/**
 * Manual ingestion API service
 * Handles batch imports from Zoho and Canvas
 */

import apiClient from './client';

export interface IngestRequest {
  sourceId?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
  testMode?: boolean;
}

export interface IngestResponse {
  status: 'processing' | 'test_complete' | 'success' | 'failed';
  source: string;
  recordsFetched: number;
  recordsProcessed: number;
  recordsFailed: number;
  errors: string[];
  preview?: any[];
  jobId?: string;
}

export interface JobStatus {
  id: string;
  status: 'pending' | 'processing' | 'complete' | 'failed';
  source: string;
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
  startedAt: string;
  completedAt?: string;
  errors?: string[];
  summary?: {
    recordsFetched: number;
    recordsProcessed: number;
    recordsFailed: number;
  };
}

export const ingestApi = {
  /**
   * Trigger manual ingestion from Zoho Surveys
   */
  async ingestZohoData(request: IngestRequest) {
    const response = await apiClient.post<IngestResponse>(
      '/api/ingest/zoho',
      request
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Trigger manual ingestion from Canvas LMS
   */
  async ingestCanvasData(request: IngestRequest) {
    const response = await apiClient.post<IngestResponse>(
      '/api/ingest/canvas',
      request
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Check status of an ingestion job
   */
  async getJobStatus(jobId: string) {
    const response = await apiClient.get<JobStatus>(
      `/api/ingest/status/${jobId}`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Manual data entry (for testing)
   */
  async manualEntry(data: any) {
    const response = await apiClient.post<{
      status: string;
      recordId: string;
      message: string;
    }>('/api/ingest/manual', data);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get recent ingestion jobs
   */
  async getRecentJobs(limit: number = 10) {
    const response = await apiClient.get<{
      jobs: JobStatus[];
    }>('/api/ingest/jobs/recent', { limit });

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Test connection to external services
   */
  async testConnection(service: 'zoho' | 'canvas') {
    const response = await apiClient.get<{
      service: string;
      connected: boolean;
      message: string;
      details?: any;
    }>(`/api/ingest/test/${service}`);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },
};