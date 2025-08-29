/**
 * Issue Analysis Service
 * Categorizes and analyzes course issues
 */

export interface ActionItem {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  estimatedEffort: string;
  impactScore: number;
  course: string;
}

export interface CourseIssueAnalysis {
  courseId: string;
  courseName: string;
  totalIssues: number;
  criticalIssues: number;
  actionItems: ActionItem[];
  overallSeverity: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
}

export interface IssueCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

export const ISSUE_CATEGORIES: Record<string, IssueCategory> = {
  content: {
    id: 'content',
    name: 'Content Quality',
    description: 'Issues related to course content and materials',
    icon: '📚',
    color: 'blue'
  },
  technical: {
    id: 'technical',
    name: 'Technical Issues',
    description: 'Platform, video, or technical problems',
    icon: '⚙️',
    color: 'red'
  },
  engagement: {
    id: 'engagement',
    name: 'Student Engagement',
    description: 'Participation and interaction concerns',
    icon: '👥',
    color: 'green'
  },
  assessment: {
    id: 'assessment',
    name: 'Assessment',
    description: 'Grading and evaluation issues',
    icon: '📝',
    color: 'purple'
  },
  communication: {
    id: 'communication',
    name: 'Communication',
    description: 'Instructor-student communication problems',
    icon: '💬',
    color: 'orange'
  },
  accessibility: {
    id: 'accessibility',
    name: 'Accessibility',
    description: 'Accessibility and inclusion concerns',
    icon: '♿',
    color: 'teal'
  }
};

export class IssueAnalysisService {
  static analyzeIssues(reviews: any[]): CourseIssueAnalysis[] {
    // Mock implementation for demo
    return [];
  }

  static categorizeIssue(issueText: string): string {
    const text = issueText.toLowerCase();
    
    if (text.includes('video') || text.includes('technical') || text.includes('platform')) {
      return 'technical';
    }
    if (text.includes('content') || text.includes('material') || text.includes('curriculum')) {
      return 'content';
    }
    if (text.includes('engagement') || text.includes('participation') || text.includes('interaction')) {
      return 'engagement';
    }
    if (text.includes('grade') || text.includes('assessment') || text.includes('exam')) {
      return 'assessment';
    }
    if (text.includes('communication') || text.includes('response') || text.includes('feedback')) {
      return 'communication';
    }
    if (text.includes('accessibility') || text.includes('disability') || text.includes('accommodation')) {
      return 'accessibility';
    }
    
    return 'content'; // default
  }

  static prioritizeIssues(issues: any[]): ActionItem[] {
    return issues.map((issue, index) => ({
      id: `action_${index}`,
      title: issue.title || 'Course Improvement',
      description: issue.description || 'Address course feedback',
      priority: issue.priority || 'medium',
      category: this.categorizeIssue(issue.description || ''),
      estimatedEffort: '2-4 hours',
      impactScore: Math.random() * 10,
      course: issue.course || 'Unknown Course'
    }));
  }
}