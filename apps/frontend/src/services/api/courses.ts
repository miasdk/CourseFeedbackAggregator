/**
 * Course API service
 * Handles all course-related API calls
 */

import apiClient from './client';
import type { Course, CourseDetail, CourseStats } from '../../shared/types/course';

export const courseApi = {
  /**
   * Get all courses with optional filters
   */
  async getCourses(filters?: {
    status?: string;
    hasShowstoppers?: boolean;
    minResponses?: number;
  }) {
    const response = await apiClient.get<{
      courses: Course[];
      total: number;
    }>('/api/courses', filters);

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get detailed information for a specific course
   */
  async getCourseDetail(courseId: string) {
    const response = await apiClient.get<CourseDetail>(
      `/api/courses/${courseId}`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Get course statistics
   */
  async getCourseStats(courseId: string) {
    const response = await apiClient.get<CourseStats>(
      `/api/courses/${courseId}/stats`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Update course mapping to Canvas
   */
  async updateCourseMapping(courseId: string, canvasId: string) {
    const response = await apiClient.put(
      `/api/courses/${courseId}/mapping`,
      { canvas_id: canvasId }
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },

  /**
   * Sync course data from Canvas
   */
  async syncFromCanvas(courseId: string) {
    const response = await apiClient.post(
      `/api/courses/${courseId}/sync`
    );

    if (response.error) {
      throw new Error(response.error);
    }

    return response.data;
  },
};