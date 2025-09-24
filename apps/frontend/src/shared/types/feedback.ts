/**
 * Feedback and survey response type definitions
 * Aligned with backend database schema
 */

export interface SurveyResponse {
  id: string;
  sourceType: 'zoho_survey' | 'canvas_lms';
  sourceResponseId: string;
  courseId: number;
  courseNameRaw: string;
  reviewerEmail: string;
  rawPayload: Record<string, any>;
  processedAt: string;
  feedbackSections: FeedbackSection[];
  course?: {
    id: number;
    courseName: string;
    department: string;
  };
}

export interface FeedbackSection {
  id: string;
  surveyResponseId: string;
  sectionType: string;
  sectionName: string;
  rating: number;
  positiveFeedback: string;
  improvementSuggestions: string;
  isShowstopper: boolean;
  showstopperDetails?: string;
  metadata?: {
    extractedThemes?: string[];
    sentiment?: 'positive' | 'negative' | 'neutral';
    urgencyKeywords?: string[];
  };
}

export interface FeedbackStats {
  overview: {
    totalResponses: number;
    totalShowstoppers: number;
    averageRating: number;
    responseRate: number;
  };
  bySource: {
    zoho: {
      count: number;
      lastResponse: string;
      averageRating: number;
    };
    canvas: {
      count: number;
      lastResponse: string;
      averageRating: number;
    };
  };
  byCourse: Array<{
    courseId: number;
    courseName: string;
    responseCount: number;
    averageRating: number;
    showstopperCount: number;
  }>;
  timeDistribution: Array<{
    date: string;
    count: number;
    averageRating: number;
  }>;
  ratingDistribution: Record<number, number>;
  showstopperTrends: Array<{
    date: string;
    count: number;
    resolvedCount: number;
  }>;
}

export interface FeedbackFilter {
  courseId?: number;
  sourceType?: 'zoho_survey' | 'canvas_lms';
  dateRange?: {
    start: string;
    end: string;
  };
  ratingRange?: [number, number];
  showstoppersOnly?: boolean;
  sectionTypes?: string[];
  searchTerm?: string;
}

export interface FeedbackAnalysis {
  themes: Array<{
    name: string;
    frequency: number;
    sentiment: 'positive' | 'negative' | 'neutral';
    examples: string[];
    courses: string[];
  }>;
  sentiment: {
    positive: number;
    negative: number;
    neutral: number;
  };
  urgencyKeywords: Array<{
    keyword: string;
    frequency: number;
    contexts: string[];
  }>;
  showstopperPatterns: Array<{
    pattern: string;
    frequency: number;
    affectedCourses: number;
    description: string;
  }>;
}

export interface ShowstopperIssue extends FeedbackSection {
  priority: 'critical' | 'high' | 'medium' | 'low';
  affectedCourses: string[];
  firstReported: string;
  lastReported: string;
  frequency: number;
  status: 'open' | 'in_progress' | 'resolved' | 'wont_fix';
  resolution?: {
    resolvedAt: string;
    resolvedBy: string;
    notes: string;
    actions: string[];
  };
}