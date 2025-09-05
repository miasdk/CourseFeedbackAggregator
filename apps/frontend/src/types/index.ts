// Minimal types - only what we're currently using

// Core Course interface without circular dependencies
export interface Course {
  id: string;
  title: string;
  category: string;
  rating: number;
  reviewCount: number;
  moduleCount: number;
  lastUpdated: string;
  lastUpdatedDate: Date;
  criticalIssues: number;
  description?: string;
  instructor?: string;
  duration?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  issues?: string[];
  priorityLevel?: 'urgent' | 'high' | 'medium' | 'low';
  // Smart Filtering Extensions (optional, type-safe)
  issueAnalysis?: any;
  actionItems?: any[];
  issueCategories?: string[];
  analyticsData?: {
    averageRating: number;
    totalReviews: number;
    issueCount: number;
    quickWinPotential: number;
    priorityScore: number;
    tags: string[];
    lastUpdated: string;
  };
}

// Keep existing API types from services/api.ts
export interface Feedback {
  id: string;
  course_name: string;
  instructor: string;
  rating: number;
  students_affected: number;
  priority: string;
  issues: string[];
  date: string;
  impact_score?: number;
  urgency_score?: number;
  effort_score?: number;
  total_score?: number;
}

export interface Priority {
  id: string;
  course: string;
  issue: string;
  priority: number;
}

export interface Stats {
  totalCourses: number;
  averageRating: number;
  criticalIssues: number;
  pendingReviews: number;
}