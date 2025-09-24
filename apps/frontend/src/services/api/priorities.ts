/**
 * Priority API service
 * Handles priority scoring and recommendations
 */

import apiClient from './client';
import type {
  CoursePriority,
  Recommendation,
  ScoringWeights,
  PriorityExplanation
} from '../../shared/types/priority';

export const priorityApi = {
  /**
   * Get priority recommendations
   */
  async getRecommendations(params?: {
    limit?: number;
    minScore?: number;
    includeExplanations?: boolean;
  }) {
    const response = await apiClient.get<{
      recommendations: Recommendation[];
      weights: ScoringWeights;
    }>('/api/priorities/recommendations', params);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get course priorities
   */
  async getCoursePriorities(params?: {
    sortBy?: 'priority' | 'impact' | 'urgency' | 'effort';
    order?: 'asc' | 'desc';
  }) {
    const response = await apiClient.get<{
      priorities: CoursePriority[];
    }>('/api/priorities', params);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get detailed priority explanation for a course
   */
  async getPriorityExplanation(courseId: string) {
    const response = await apiClient.get<PriorityExplanation>(
      `/api/priorities/${courseId}/explanation`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get current scoring weights
   */
  async getScoringWeights() {
    const response = await apiClient.get<ScoringWeights>(
      '/api/priorities/weights'
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Update scoring weights
   */
  async updateScoringWeights(weights: Partial<ScoringWeights>) {
    const response = await apiClient.put<{
      weights: ScoringWeights;
      message: string;
    }>('/api/priorities/weights', weights);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Recalculate all priorities with new weights
   */
  async recalculatePriorities(weights?: Partial<ScoringWeights>) {
    const response = await apiClient.post<{
      updated: number;
      priorities: CoursePriority[];
    }>('/api/priorities/recalculate', weights);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Save a custom weight configuration
   */
  async saveWeightConfiguration(config: {
    name: string;
    weights: ScoringWeights;
    description?: string;
  }) {
    const response = await apiClient.post<{
      id: string;
      message: string;
    }>('/api/priorities/weights/save', config);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get saved weight configurations
   */
  async getWeightConfigurations() {
    const response = await apiClient.get<{
      configurations: Array<{
        id: string;
        name: string;
        weights: ScoringWeights;
        description?: string;
        isActive: boolean;
        createdAt: string;
      }>;
    }>('/api/priorities/weights/configurations');

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },
};