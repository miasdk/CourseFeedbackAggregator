export interface ScoringWeights {
  impact: number;
  urgency: number;
  effort: number;
  strategic: number;
  trend: number;
}

export interface Recommendation {
  id: string;
  course_id: string;
  course_name: string;
  title: string;
  description: string;
  category: 'content' | 'technical' | 'navigation' | 'assessment' | 'other';
  priority_score: number;
  impact_score: number;
  urgency_score: number;
  effort_score: number;
  strategic_score: number;
  trend_score: number;
  affected_students: number;
  feedback_count: number;
  is_show_stopper: boolean;
  created_at: string;
  status: 'pending' | 'validated' | 'in_progress' | 'resolved';
  validator?: string;
  validation_notes?: string;
}

export interface DataSourceStatus {
  canvas: {
    connected: boolean;
    last_sync: string;
    courses_synced: number;
    feedback_items: number;
  };
  zoho: {
    connected: boolean;
    last_sync: string;
    surveys_synced: number;
    responses: number;
  };
}

export interface FeedbackItem {
  id: string;
  course_id: string;
  student_name?: string;
  student_email?: string;
  feedback_text: string;
  rating: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source: 'canvas' | 'zoho';
  source_id: string;
  created_at: string;
}

// Legacy Course interface for backward compatibility with existing components
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
  description: string;
  instructor: string;
  duration: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  priorityLevel: 'urgent' | 'high' | 'medium' | 'low';
  issues: string[];
  analyticsData: {
    averageRating: number;
    totalReviews: number;
    issueCount: number;
    quickWinPotential: number;
    priorityScore: number;
    tags: string[];
    lastUpdated: string;
  };
}