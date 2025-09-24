/**
 * Feedback API service
 * Handles survey responses and feedback sections
 */

import apiClient from './client';
import type {
  SurveyResponse,
  FeedbackSection,
  FeedbackStats
} from '../../shared/types/feedback';

export const feedbackApi = {
  /**
   * Get all feedback for a course
   */
  async getCourseFeedback(courseId: string, params?: {
    startDate?: string;
    endDate?: string;
    showstoppersOnly?: boolean;
    limit?: number;
    offset?: number;
  }) {
    const response = await apiClient.get<{
      feedback: SurveyResponse[];
      total: number;
      hasMore: boolean;
    }>(`/api/feedback/course/${courseId}`, params);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get a specific survey response
   */
  async getSurveyResponse(responseId: string) {
    const response = await apiClient.get<SurveyResponse>(
      `/api/feedback/response/${responseId}`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get feedback statistics
   */
  async getFeedbackStats(params?: {
    courseId?: string;
    dateRange?: string;
  }) {
    const response = await apiClient.get<FeedbackStats>(
      '/api/feedback/stats',
      params
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get showstopper feedback across all courses
   */
  async getShowstoppers(params?: {
    limit?: number;
    resolved?: boolean;
  }) {
    const response = await apiClient.get<{
      showstoppers: FeedbackSection[];
      total: number;
    }>('/api/feedback/showstoppers', params);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Mark a showstopper as resolved
   */
  async resolveShowstopper(feedbackId: string, resolution: {
    resolved: boolean;
    notes?: string;
  }) {
    const response = await apiClient.patch(
      `/api/feedback/${feedbackId}/resolve`,
      resolution
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get recent feedback entries
   */
  async getRecentFeedback(limit: number = 10) {
    const response = await apiClient.get<{
      feedback: SurveyResponse[];
    }>('/api/feedback/recent', { limit });

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },
};