/**
 * Course-related type definitions
 * Aligned with backend database schema
 */

export interface Course {
  id: number;
  courseId: string;
  courseName: string;
  instructorName: string;
  department: string;
  semester: string;
  enrollmentCount: number;
  isActive: boolean;
  canvasUrl?: string;
  lastSyncedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CourseDetail extends Course {
  description?: string;
  syllabus?: string;
  sections: CourseSection[];
  feedbackSummary: {
    totalResponses: number;
    averageRating: number;
    showstopperCount: number;
    lastResponseAt?: string;
  };
  priorityInfo?: {
    score: number;
    rank: number;
    lastCalculatedAt: string;
  };
}

export interface CourseSection {
  id: string;
  name: string;
  sectionNumber: string;
  enrollmentCount: number;
  meetingTimes: string[];
}

export interface CourseStats {
  courseId: string;
  courseName: string;
  totalResponses: number;
  responseRate: number;
  averageRating: number;
  ratingDistribution: Record<number, number>;
  showstopperCount: number;
  commonThemes: Array<{
    theme: string;
    frequency: number;
    sentiment: 'positive' | 'negative' | 'neutral';
  }>;
  sectionBreakdown: Array<{
    sectionType: string;
    averageRating: number;
    responseCount: number;
  }>;
  trendsOverTime: Array<{
    date: string;
    averageRating: number;
    responseCount: number;
  }>;
}

export interface CourseMapping {
  id: string;
  surveyCourseId: string;
  surveyCourseName: string;
  canvasId: number;
  confidenceScore: number;
  mappingMethod: 'manual' | 'automatic' | 'fuzzy_match';
  verifiedAt?: string;
  verifiedBy?: string;
}

export interface CourseFilter {
  status?: 'active' | 'inactive' | 'all';
  department?: string;
  semester?: string;
  hasShowstoppers?: boolean;
  minResponses?: number;
  ratingRange?: [number, number];
  searchTerm?: string;
}

export interface CourseSortOption {
  field: 'courseName' | 'department' | 'enrollmentCount' | 'averageRating' | 'responseCount' | 'lastResponseAt';
  direction: 'asc' | 'desc';
}