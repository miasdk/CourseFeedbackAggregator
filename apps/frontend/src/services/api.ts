/**
 * API Service for Course Feedback Aggregator
 * Connects to FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface Feedback {
  id: string;
  course_name: string;
  rating: number;
  feedback: string;
  issues: string[];
  priority: string;
  source: string;
  impact_score?: number;
  urgency_score?: number;
  effort_score?: number;
  total_score?: number;
  students_affected?: number;
  date?: string;
}

export interface Priority {
  id: string;
  course: string;
  recommendation: string;
  priority_score: number;
  impact: number;
  urgency: number;
  effort: number;
  source: string;
  why: string;
  students_affected?: number;
}

export interface Stats {
  total_courses: number;
  total_feedback: number;
  urgent_issues: number;
  high_priority: number;
  avg_rating: number;
  sources: {
    canvas: number;
    zoho: number;
  };
}

class APIService {
  async getFeedback(): Promise<Feedback[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback`);
      if (!response.ok) throw new Error('Failed to fetch feedback');
      return await response.json();
    } catch (error) {
      console.error('Error fetching feedback:', error);
      return [];
    }
  }

  async getPriorities(): Promise<Priority[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/priorities`);
      if (!response.ok) throw new Error('Failed to fetch priorities');
      return await response.json();
    } catch (error) {
      console.error('Error fetching priorities:', error);
      return [];
    }
  }

  async getStats(): Promise<Stats | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      return await response.json();
    } catch (error) {
      console.error('Error fetching stats:', error);
      return null;
    }
  }

  async recomputeScores(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/recompute`, {
        method: 'POST',
      });
      return response.ok;
    } catch (error) {
      console.error('Error recomputing scores:', error);
      return false;
    }
  }
}

export default new APIService();