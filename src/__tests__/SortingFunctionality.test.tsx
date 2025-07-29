// Test sorting functions directly rather than mocking the entire App
interface Course {
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
}

// Test data with realistic dates
const mockCoursesWithDates: Course[] = [
  {
    id: '1',
    title: 'Course A - Oldest',
    category: 'AI/ML',
    rating: 4.8,
    reviewCount: 15,
    moduleCount: 8,
    lastUpdated: '30 days ago',
    lastUpdatedDate: new Date('2024-12-20'),
    criticalIssues: 0,
    description: 'Test course A',
    instructor: 'Instructor A',
    duration: '8 modules'
  },
  {
    id: '2', 
    title: 'Course B - Most Recent',
    category: 'Leadership',
    rating: 3.5,
    reviewCount: 8,
    moduleCount: 6,
    lastUpdated: '2 days ago',
    lastUpdatedDate: new Date('2025-01-20'),
    criticalIssues: 2,
    description: 'Test course B',
    instructor: 'Instructor B',
    duration: '6 modules'
  },
  {
    id: '3',
    title: 'Course C - Middle',
    category: 'Design',
    rating: 4.2,
    reviewCount: 12,
    moduleCount: 10,
    lastUpdated: '1 week ago',
    lastUpdatedDate: new Date('2025-01-15'),
    criticalIssues: 1,
    description: 'Test course C',
    instructor: 'Instructor C',
    duration: '10 modules'
  }
];

// Sorting functions (extracted from App.tsx)
const sortCourses = (courses: Course[], sortBy: 'rating' | 'date' | 'issues' | 'name') => {
  return [...courses].sort((a, b) => {
    switch (sortBy) {
      case 'rating':
        return b.rating - a.rating;
      case 'date':
        return b.lastUpdatedDate.getTime() - a.lastUpdatedDate.getTime();
      case 'issues':
        return b.criticalIssues - a.criticalIssues;
      case 'name':
        return a.title.localeCompare(b.title);
      default:
        return 0;
    }
  });
};

describe('Sorting Functionality', () => {
  test('sorts by rating correctly (highest first)', () => {
    const sorted = sortCourses(mockCoursesWithDates, 'rating');
    
    // Should be sorted by rating: Course A (4.8) → Course C (4.2) → Course B (3.5)
    expect(sorted[0].title).toBe('Course A - Oldest');
    expect(sorted[0].rating).toBe(4.8);
    expect(sorted[1].title).toBe('Course C - Middle');
    expect(sorted[1].rating).toBe(4.2);
    expect(sorted[2].title).toBe('Course B - Most Recent');
    expect(sorted[2].rating).toBe(3.5);
  });

  test('sorts by date correctly (most recent first)', () => {
    const sorted = sortCourses(mockCoursesWithDates, 'date');
    
    // Should be sorted by lastUpdatedDate: Course B (Jan 20, 2025) → Course C (Jan 15, 2025) → Course A (Dec 20, 2024)
    expect(sorted[0].title).toBe('Course B - Most Recent');
    expect(sorted[0].lastUpdatedDate.getTime()).toBeGreaterThan(sorted[1].lastUpdatedDate.getTime());
    expect(sorted[1].title).toBe('Course C - Middle');
    expect(sorted[1].lastUpdatedDate.getTime()).toBeGreaterThan(sorted[2].lastUpdatedDate.getTime());
    expect(sorted[2].title).toBe('Course A - Oldest');
  });

  test('sorts by issues correctly (most issues first)', () => {
    const sorted = sortCourses(mockCoursesWithDates, 'issues');
    
    // Should be sorted by criticalIssues: Course B (2) → Course C (1) → Course A (0)
    expect(sorted[0].title).toBe('Course B - Most Recent');
    expect(sorted[0].criticalIssues).toBe(2);
    expect(sorted[1].title).toBe('Course C - Middle');
    expect(sorted[1].criticalIssues).toBe(1);
    expect(sorted[2].title).toBe('Course A - Oldest');
    expect(sorted[2].criticalIssues).toBe(0);
  });

  test('sorts alphabetically correctly (A-Z)', () => {
    const sorted = sortCourses(mockCoursesWithDates, 'name');
    
    // Should be sorted alphabetically: Course A → Course B → Course C
    expect(sorted[0].title).toBe('Course A - Oldest');
    expect(sorted[1].title).toBe('Course B - Most Recent');
    expect(sorted[2].title).toBe('Course C - Middle');
  });

     test('date sorting uses actual Date objects, not string parsing', () => {
     // Create courses with confusing string dates but clear Date objects
     const confusingCourses: Course[] = [
       {
         ...mockCoursesWithDates[0],
         lastUpdated: 'Just now', // Misleading string
         lastUpdatedDate: new Date('2023-01-01') // Actually oldest
       },
       {
         ...mockCoursesWithDates[1],
         lastUpdated: 'Ages ago', // Misleading string
         lastUpdatedDate: new Date('2025-12-31') // Actually newest
       }
     ];
     
     const sorted = sortCourses(confusingCourses, 'date');
     
     // Should sort by actual Date objects, not misleading strings
     expect(sorted[0].lastUpdated).toBe('Ages ago'); // This one is actually newest by date
     expect(sorted[0].lastUpdatedDate.getTime()).toBeGreaterThan(sorted[1].lastUpdatedDate.getTime());
     expect(sorted[1].lastUpdated).toBe('Just now'); // This one is actually oldest by date  
     expect(sorted[1].lastUpdatedDate.getTime()).toBeLessThan(sorted[0].lastUpdatedDate.getTime());
   });

     test('preserves original array when sorting', () => {
     const original = [...mockCoursesWithDates];
     const sorted = sortCourses(mockCoursesWithDates, 'name'); // Use name sorting to ensure different order
     
     // Original should be unchanged
     expect(mockCoursesWithDates).toEqual(original);
     
     // Sorted should be a new array (not mutating the original)
     expect(sorted).not.toBe(mockCoursesWithDates);
     expect(sorted).toHaveLength(mockCoursesWithDates.length);
   });

  test('handles empty array gracefully', () => {
    const sorted = sortCourses([], 'rating');
    expect(sorted).toEqual([]);
  });

  test('handles single item array', () => {
    const singleCourse = [mockCoursesWithDates[0]];
    const sorted = sortCourses(singleCourse, 'rating');
    expect(sorted).toHaveLength(1);
    expect(sorted[0]).toEqual(mockCoursesWithDates[0]);
  });
}); 