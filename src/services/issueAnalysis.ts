// Issue Analysis Service - Smart Filtering & Auto-Action Generation
// Analyzes review text to categorize issues and generate action items

export interface IssueCategory {
  id: string;
  name: string;
  icon: string;
  color: string;
  description: string;
}

export interface ActionItem {
  id: string;
  title: string;
  description: string;
  category: IssueCategory;
  priority: 'urgent' | 'high' | 'medium' | 'low';
  impact: number; // 1-10 scale
  effort: number; // 1-10 scale (complexity to implement)
  priorityScore: number; // calculated: impact / effort
  affectedModules: string[];
  suggestedSolution: string;
  reviewReferences: string[]; // review IDs that contributed to this action
}

export interface CourseIssueAnalysis {
  courseId: string;
  totalReviews: number;
  criticalIssues: number;
  actionItems: ActionItem[];
  issueBreakdown: {
    [categoryId: string]: {
      count: number;
      severity: 'low' | 'medium' | 'high' | 'critical';
      examples: string[];
    };
  };
  lastAnalyzed: Date;
}

// Issue Categories - Based on PRD requirements
export const ISSUE_CATEGORIES: { [key: string]: IssueCategory } = {
  TECHNICAL: {
    id: 'technical',
    name: 'Technical Issues',
    icon: '🔧',
    color: 'red',
    description: 'Audio/video problems, platform glitches, technical barriers'
  },
  CONTENT: {
    id: 'content',
    name: 'Content Issues',
    icon: '📝',
    color: 'orange',
    description: 'Outdated examples, missing materials, inaccurate information'
  },
  INSTRUCTIONAL: {
    id: 'instructional',
    name: 'Instructional Issues',
    icon: '👨‍🎓',
    color: 'yellow',
    description: 'Unclear explanations, pacing problems, learning objectives'
  },
  UX: {
    id: 'ux',
    name: 'UX Issues',
    icon: '🎨',
    color: 'blue',
    description: 'Navigation problems, accessibility issues, user interface'
  },
  ENGAGEMENT: {
    id: 'engagement',
    name: 'Engagement Issues',
    icon: '⚡',
    color: 'purple',
    description: 'Boring content, lack of interaction, motivation problems'
  }
};

// Text analysis patterns for automatic categorization
const ISSUE_PATTERNS = {
  TECHNICAL: [
    /audio.*(?:problem|issue|broken|not work|quiet|loud|distorted)/i,
    /video.*(?:problem|issue|broken|not.*play|loading|buffering|quality)/i,
    /platform.*(?:glitch|bug|error|crash|freeze)/i,
    /technical.*(?:issue|problem|difficulty|error)/i,
    /login.*(?:problem|issue|not work|error)/i,
    /access.*(?:denied|problem|issue|not work)/i,
    /link.*(?:broken|not work|dead|404)/i
  ],
  CONTENT: [
    /outdated.*(?:example|information|material|content)/i,
    /missing.*(?:material|content|resource|file|document)/i,
    /inaccurate.*(?:information|data|example)/i,
    /wrong.*(?:information|data|example|link)/i,
    /need.*(?:updated|current|recent).*(?:example|material|content)/i,
    /example.*(?:outdated|old|irrelevant)/i,
    /material.*(?:missing|incomplete|lacking)/i
  ],
  INSTRUCTIONAL: [
    /unclear.*(?:explanation|instruction|direction)/i,
    /confusing.*(?:explanation|instruction|concept)/i,
    /too.*(?:fast|slow|quick|rushed)/i,
    /pacing.*(?:problem|issue|too.*fast|too.*slow)/i,
    /need.*(?:more.*explanation|clearer.*instruction|better.*example)/i,
    /difficult.*(?:to.*understand|to.*follow|concept)/i,
    /instructor.*(?:unclear|confusing|hard.*to.*understand)/i
  ],
  UX: [
    /navigation.*(?:problem|difficult|confusing|poor)/i,
    /interface.*(?:problem|confusing|poor|difficult)/i,
    /hard.*to.*(?:navigate|find|locate)/i,
    /accessibility.*(?:problem|issue|concern)/i,
    /design.*(?:poor|confusing|outdated)/i,
    /layout.*(?:confusing|poor|difficult)/i,
    /user.*experience.*(?:poor|bad|frustrating)/i
  ],
  ENGAGEMENT: [
    /boring.*(?:content|material|video|lecture)/i,
    /not.*engaging.*(?:enough|content|material)/i,
    /lack.*(?:interaction|engagement|motivation)/i,
    /monotone.*(?:voice|delivery|presentation)/i,
    /need.*more.*(?:interaction|engagement|activity)/i,
    /dry.*(?:content|material|presentation)/i,
    /motivat.*(?:lacking|problem|issue)/i
  ]
};

// Priority calculation based on frequency and impact keywords
const HIGH_IMPACT_KEYWORDS = [
  'show.*stopper', 'critical', 'urgent', 'blocking', 'prevent.*progress',
  'cannot.*continue', 'major.*issue', 'serious.*problem'
];

const MEDIUM_IMPACT_KEYWORDS = [
  'important', 'should.*fix', 'need.*improvement', 'would.*help',
  'could.*be.*better', 'recommend.*change'
];

/**
 * Analyzes review text to categorize issues and generate action items
 */
export class IssueAnalysisService {
  
  /**
   * Analyze a single review and categorize its issues
   */
  static analyzeReview(review: {
    positive_comments?: string;
    improvement_opportunities?: string;
    show_stopper_details?: string;
    is_show_stopper?: boolean;
    rating: number;
  }): { categories: string[], severity: 'low' | 'medium' | 'high' | 'critical', suggestions: string[] } {
    
    const text = [
      review.improvement_opportunities || '',
      review.show_stopper_details || ''
    ].join(' ').toLowerCase();

    const categories: string[] = [];
    const suggestions: string[] = [];
    
    // Categorize based on text patterns
    Object.entries(ISSUE_PATTERNS).forEach(([category, patterns]) => {
      const hasMatch = patterns.some(pattern => pattern.test(text));
      if (hasMatch) {
        categories.push(category.toLowerCase());
      }
    });
    
    // Determine severity
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
    
    if (review.is_show_stopper) {
      severity = 'critical';
    } else if (HIGH_IMPACT_KEYWORDS.some(keyword => new RegExp(keyword, 'i').test(text))) {
      severity = 'high';
    } else if (MEDIUM_IMPACT_KEYWORDS.some(keyword => new RegExp(keyword, 'i').test(text))) {
      severity = 'medium';
    } else if (review.rating <= 2) {
      severity = 'high';
    } else if (review.rating <= 3) {
      severity = 'medium';
    }
    
    // Generate suggestions based on patterns
    if (categories.includes('technical')) {
      suggestions.push('Review and test all technical components', 'Check audio/video quality', 'Verify all links and platform functionality');
    }
    if (categories.includes('content')) {
      suggestions.push('Update outdated examples and materials', 'Review content accuracy', 'Add missing resources');
    }
    if (categories.includes('instructional')) {
      suggestions.push('Clarify confusing explanations', 'Adjust pacing based on feedback', 'Add more examples');
    }
    if (categories.includes('ux')) {
      suggestions.push('Improve navigation and user interface', 'Test accessibility features', 'Simplify user flows');
    }
    if (categories.includes('engagement')) {
      suggestions.push('Add interactive elements', 'Vary presentation style', 'Include more engaging activities');
    }
    
    return { categories, severity, suggestions };
  }
  
  /**
   * Generate action items for a course based on all its reviews
   */
  static generateActionItems(reviews: any[], courseId: string): ActionItem[] {
    const actionItems: ActionItem[] = [];
    const issueFrequency: { [category: string]: { count: number, examples: string[], suggestions: Set<string> } } = {};
    
    // Analyze all reviews
    reviews.forEach((review, index) => {
      const analysis = this.analyzeReview(review);
      
      analysis.categories.forEach(category => {
        if (!issueFrequency[category]) {
          issueFrequency[category] = { count: 0, examples: [], suggestions: new Set() };
        }
        issueFrequency[category].count++;
        
        // Add example text (truncated)
        const exampleText = review.improvement_opportunities || review.show_stopper_details || '';
        if (exampleText && issueFrequency[category].examples.length < 3) {
          issueFrequency[category].examples.push(exampleText.substring(0, 100) + '...');
        }
        
        // Add suggestions
        analysis.suggestions.forEach(suggestion => {
          issueFrequency[category].suggestions.add(suggestion);
        });
      });
    });
    
    // Generate action items based on frequency and impact
    Object.entries(issueFrequency).forEach(([categoryId, data]) => {
      if (data.count === 0) return;
      
      const category = ISSUE_CATEGORIES[categoryId.toUpperCase()];
      if (!category) return;
      
      const frequency = data.count / reviews.length;
      const impact = Math.min(10, Math.floor(frequency * 10) + (data.count > 5 ? 2 : 0));
      const effort = this.estimateEffort(categoryId, data.count);
      const priorityScore = impact / effort;
      
      let priority: 'urgent' | 'high' | 'medium' | 'low' = 'low';
      if (priorityScore >= 2.5) priority = 'urgent';
      else if (priorityScore >= 1.5) priority = 'high';
      else if (priorityScore >= 0.75) priority = 'medium';
      
      actionItems.push({
        id: `${courseId}-${categoryId}-${Date.now()}`,
        title: `Address ${category.name}`,
        description: `${data.count} reviews (${(frequency * 100).toFixed(0)}%) mentioned ${category.name.toLowerCase()}`,
        category,
        priority,
        impact,
        effort,
        priorityScore,
        affectedModules: [], // TODO: Extract from review module_name
        suggestedSolution: Array.from(data.suggestions).join('; '),
        reviewReferences: [] // TODO: Add review IDs
      });
    });
    
    // Sort by priority score (highest first)
    return actionItems.sort((a, b) => b.priorityScore - a.priorityScore);
  }
  
  /**
   * Estimate effort required to fix issues in a category
   */
  private static estimateEffort(categoryId: string, frequency: number): number {
    const baseEffort: { [key: string]: number } = {
      'technical': 8, // Usually requires development work
      'content': 4,   // Content updates are moderate effort  
      'instructional': 6, // Requires instructional design
      'ux': 7,        // UI/UX changes need design + dev
      'engagement': 5  // Creative work, moderate effort
    };
    
    const base = baseEffort[categoryId] || 5;
    
    // More frequent issues may require more systematic solutions
    const frequencyMultiplier = frequency > 10 ? 1.5 : (frequency > 5 ? 1.2 : 1.0);
    
    return Math.min(10, Math.floor(base * frequencyMultiplier));
  }
} 