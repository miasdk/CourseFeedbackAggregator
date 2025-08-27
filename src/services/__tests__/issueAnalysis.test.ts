import { IssueAnalysisService, ISSUE_CATEGORIES } from '../issueAnalysis';

describe('IssueAnalysisService', () => {
  const sampleReview = {
    positive_comments: 'Good course content',
    improvement_opportunities: 'The audio quality was poor and some video links were broken',
    show_stopper_details: '',
    is_show_stopper: false,
    rating: 3
  };

  const sampleShowStopperReview = {
    positive_comments: 'Some good content',
    improvement_opportunities: '',
    show_stopper_details: 'Major technical issues prevent course completion',
    is_show_stopper: true,
    rating: 1
  };

  const sampleContentIssueReview = {
    positive_comments: 'Nice structure',
    improvement_opportunities: 'Examples are outdated and material is missing important resources',
    show_stopper_details: '',
    is_show_stopper: false,
    rating: 2
  };

  const sampleInstructionalIssueReview = {
    positive_comments: 'Good topic',
    improvement_opportunities: 'Explanation is unclear and pacing is too fast',
    show_stopper_details: '',
    is_show_stopper: false,
    rating: 2
  };

  describe('analyzeReview', () => {
    test('should categorize technical issues correctly', () => {
      const result = IssueAnalysisService.analyzeReview(sampleReview);
      
      expect(result.categories).toContain('technical');
      expect(result.suggestions).toContain('Review and test all technical components');
      expect(result.suggestions).toContain('Check audio/video quality');
    });

    test('should categorize show stopper as critical severity', () => {
      const result = IssueAnalysisService.analyzeReview(sampleShowStopperReview);
      
      expect(result.severity).toBe('critical');
      expect(result.categories).toContain('technical');
    });

    test('should categorize content issues correctly', () => {
      const result = IssueAnalysisService.analyzeReview(sampleContentIssueReview);
      
      expect(result.categories).toContain('content');
      expect(result.suggestions).toContain('Update outdated examples and materials');
      expect(result.suggestions).toContain('Add missing resources');
    });

    test('should categorize instructional issues correctly', () => {
      const result = IssueAnalysisService.analyzeReview(sampleInstructionalIssueReview);
      
      expect(result.categories).toContain('instructional');
      expect(result.suggestions).toContain('Clarify confusing explanations');
      expect(result.suggestions).toContain('Adjust pacing based on feedback');
    });

    test('should determine severity based on rating', () => {
      const lowRatingReview = { ...sampleReview, rating: 1, is_show_stopper: false };
      const mediumRatingReview = { ...sampleReview, rating: 3 };
      const highRatingReview = { ...sampleReview, rating: 4 };

      expect(IssueAnalysisService.analyzeReview(lowRatingReview).severity).toBe('high');
      expect(IssueAnalysisService.analyzeReview(mediumRatingReview).severity).toBe('medium');
      expect(IssueAnalysisService.analyzeReview(highRatingReview).severity).toBe('low');
    });

    test('should handle multiple issue categories', () => {
      const multiIssueReview = {
        positive_comments: '',
        improvement_opportunities: 'Audio is broken, examples are outdated, explanation is unclear',
        show_stopper_details: '',
        is_show_stopper: false,
        rating: 2
      };

      const result = IssueAnalysisService.analyzeReview(multiIssueReview);
      
      expect(result.categories).toContain('technical');
      expect(result.categories).toContain('content');
      expect(result.categories).toContain('instructional');
      expect(result.categories.length).toBeGreaterThan(1);
    });
  });

  describe('generateActionItems', () => {
    const sampleReviews = [
      sampleReview,
      sampleContentIssueReview,
      sampleInstructionalIssueReview,
      {
        positive_comments: 'Good',
        improvement_opportunities: 'More audio problems and video issues',
        show_stopper_details: '',
        is_show_stopper: false,
        rating: 3
      }
    ];

    test('should generate action items based on review frequency', () => {
      const actionItems = IssueAnalysisService.generateActionItems(sampleReviews, 'test-course');
      
      expect(actionItems).toHaveLength(3); // technical, content, instructional
      expect(actionItems[0]).toHaveProperty('title');
      expect(actionItems[0]).toHaveProperty('priority');
      expect(actionItems[0]).toHaveProperty('impact');
      expect(actionItems[0]).toHaveProperty('effort');
      expect(actionItems[0]).toHaveProperty('priorityScore');
    });

    test('should sort action items by priority score', () => {
      const actionItems = IssueAnalysisService.generateActionItems(sampleReviews, 'test-course');
      
      // Should be sorted by priorityScore descending
      for (let i = 0; i < actionItems.length - 1; i++) {
        expect(actionItems[i].priorityScore).toBeGreaterThanOrEqual(actionItems[i + 1].priorityScore);
      }
    });

    test('should assign correct priority levels', () => {
      const highFrequencyReviews = Array(10).fill({
        positive_comments: '',
        improvement_opportunities: 'Critical audio problems blocking progress',
        show_stopper_details: '',
        is_show_stopper: false,
        rating: 1
      });

      const actionItems = IssueAnalysisService.generateActionItems(highFrequencyReviews, 'test-course');
      
      // High frequency + high impact should result in urgent or high priority
      expect(['urgent', 'high']).toContain(actionItems[0].priority);
    });

    test('should handle empty reviews array', () => {
      const actionItems = IssueAnalysisService.generateActionItems([], 'test-course');
      expect(actionItems).toHaveLength(0);
    });

    test('should include category information in action items', () => {
      const actionItems = IssueAnalysisService.generateActionItems(sampleReviews, 'test-course');
      
      actionItems.forEach(item => {
        expect(item.category).toHaveProperty('id');
        expect(item.category).toHaveProperty('name');
        expect(item.category).toHaveProperty('icon');
        expect(item.category).toHaveProperty('color');
        expect(Object.values(ISSUE_CATEGORIES)).toContainEqual(
          expect.objectContaining({
            id: item.category.id,
            name: item.category.name
          })
        );
      });
    });

    test('should generate meaningful descriptions', () => {
      const actionItems = IssueAnalysisService.generateActionItems(sampleReviews, 'test-course');
      
      actionItems.forEach(item => {
        expect(item.description).toContain('reviews');
        expect(item.description).toMatch(/\d+%/); // Should contain percentage
        expect(item.description).toContain(item.category.name.toLowerCase());
      });
    });

    test('should calculate impact and effort appropriately', () => {
      const actionItems = IssueAnalysisService.generateActionItems(sampleReviews, 'test-course');
      
      actionItems.forEach(item => {
        expect(item.impact).toBeGreaterThanOrEqual(1);
        expect(item.impact).toBeLessThanOrEqual(10);
        expect(item.effort).toBeGreaterThanOrEqual(1);
        expect(item.effort).toBeLessThanOrEqual(10);
        expect(item.priorityScore).toBe(item.impact / item.effort);
      });
    });
  });

  describe('ISSUE_CATEGORIES', () => {
    test('should have all required categories', () => {
      const expectedCategories = ['TECHNICAL', 'CONTENT', 'INSTRUCTIONAL', 'UX', 'ENGAGEMENT'];
      
      expectedCategories.forEach(categoryKey => {
        expect(ISSUE_CATEGORIES).toHaveProperty(categoryKey);
        expect(ISSUE_CATEGORIES[categoryKey]).toHaveProperty('id');
        expect(ISSUE_CATEGORIES[categoryKey]).toHaveProperty('name');
        expect(ISSUE_CATEGORIES[categoryKey]).toHaveProperty('icon');
        expect(ISSUE_CATEGORIES[categoryKey]).toHaveProperty('color');
        expect(ISSUE_CATEGORIES[categoryKey]).toHaveProperty('description');
      });
    });

    test('should have unique category IDs', () => {
      const categoryIds = Object.values(ISSUE_CATEGORIES).map(cat => cat.id);
      const uniqueIds = Array.from(new Set(categoryIds));
      expect(categoryIds).toHaveLength(uniqueIds.length);
    });
  });
}); 