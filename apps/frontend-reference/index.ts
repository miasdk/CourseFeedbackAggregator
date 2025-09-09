export interface Course {
  id: string;
  name: string;
  instructor: string;
  enrollment: number;
  start_date: string;
  platform: 'Canvas' | 'Zoho' | 'Both';
}

export interface FeedbackItem {
  id: string;
  course_id: string;
  student_id: string;
  rating: number;
  comment: string;
  is_show_stopper: boolean;
  category: 'content' | 'technical' | 'navigation' | 'assessment' | 'other';
  source: 'Canvas' | 'Zoho';
  source_id: string;
  created_at: string;
  module_name?: string;
}

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
  related_feedback: FeedbackItem[];
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