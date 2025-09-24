/**
 * Priority scoring and recommendation type definitions
 * Aligned with backend scoring algorithm
 */

export interface CoursePriority {
  id: string;
  courseId: number;
  priorityScore: number;
  impactScore: number;
  urgencyScore: number;
  effortScore: number;
  recencyScore: number;
  totalResponses: number;
  showstopperCount: number;
  lastCalculatedAt: string;
  course?: {
    id: number;
    courseName: string;
    department: string;
    instructorName: string;
  };
}

export interface Recommendation {
  id: string;
  courseId: number;
  courseName: string;
  department: string;
  priorityScore: number;
  rank: number;
  title: string;
  description: string;
  category: 'content' | 'delivery' | 'technical' | 'logistics' | 'general';
  urgency: 'critical' | 'high' | 'medium' | 'low';
  estimatedEffort: 'low' | 'medium' | 'high';
  estimatedImpact: 'low' | 'medium' | 'high';
  affectedStudents: number;
  keyIssues: string[];
  suggestedActions: string[];
  explanation: PriorityExplanation;
  relatedFeedback: Array<{
    id: string;
    sectionName: string;
    rating: number;
    feedback: string;
    isShowstopper: boolean;
  }>;
  createdAt: string;
  updatedAt: string;
}

export interface PriorityExplanation {
  summary: string;
  factors: {
    impact: {
      score: number;
      weight: number;
      reasoning: string;
      contributors: string[];
    };
    urgency: {
      score: number;
      weight: number;
      reasoning: string;
      contributors: string[];
    };
    effort: {
      score: number;
      weight: number;
      reasoning: string;
      contributors: string[];
    };
    recency: {
      score: number;
      weight: number;
      reasoning: string;
      contributors: string[];
    };
  };
  calculation: {
    formula: string;
    breakdown: string;
    finalScore: number;
  };
  confidence: number;
  dataQuality: {
    responseCount: number;
    dataFreshness: string;
    completeness: number;
  };
}

export interface ScoringWeights {
  id?: string;
  name?: string;
  impactWeight: number;
  urgencyWeight: number;
  effortWeight: number;
  recencyWeight: number;
  isActive?: boolean;
  createdAt?: string;
  description?: string;
}

export interface WeightConfiguration {
  id: string;
  name: string;
  description: string;
  weights: ScoringWeights;
  isActive: boolean;
  isDefault: boolean;
  createdBy: string;
  createdAt: string;
  usage: {
    timesUsed: number;
    lastUsedAt?: string;
  };
}

export interface PriorityTrend {
  courseId: number;
  courseName: string;
  dataPoints: Array<{
    date: string;
    score: number;
    rank: number;
    responseCount: number;
    showstopperCount: number;
  }>;
  trend: 'improving' | 'declining' | 'stable';
  changePercent: number;
  projectedScore?: number;
}

export interface PriorityMetrics {
  totalCourses: number;
  averageScore: number;
  highPriority: number; // count of courses with score > 0.7
  mediumPriority: number; // count with score 0.4-0.7
  lowPriority: number; // count with score < 0.4
  scoreDistribution: Record<string, number>; // score ranges
  departmentBreakdown: Array<{
    department: string;
    averageScore: number;
    courseCount: number;
    highPriorityCount: number;
  }>;
  trendsOverTime: Array<{
    date: string;
    averageScore: number;
    highPriorityCount: number;
  }>;
}