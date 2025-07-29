import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import PriorityDashboard from '../StatsCards';

const mockCourses = [
  {
    id: '1',
    title: 'Test Course 1',
    category: 'AI/ML',
    rating: 3.2,
    reviewCount: 5,
    moduleCount: 8,
    lastUpdated: '2 days ago',
    criticalIssues: 2,
    description: 'Test description',
    instructor: 'Test Instructor',
    duration: '8 modules'
  },
  {
    id: '2',
    title: 'Test Course 2',
    category: 'Leadership',
    rating: 4.8,
    reviewCount: 12,
    moduleCount: 6,
    lastUpdated: '1 week ago',
    criticalIssues: 0,
    description: 'Another test course',
    instructor: 'Another Instructor',
    duration: '6 modules'
  },
  {
    id: '3',
    title: 'Test Course 3',
    category: 'Design',
    rating: 4.2,
    reviewCount: 8,
    moduleCount: 4,
    lastUpdated: '3 days ago',
    criticalIssues: 1,
    description: 'Design course',
    instructor: 'Design Instructor',
    duration: '4 modules'
  }
];

describe('PriorityDashboard', () => {
  test('renders action cards correctly', () => {
    render(<PriorityDashboard courses={mockCourses} />);
    
    // Check if all action types are rendered
    expect(screen.getByText('URGENT ACTIONS')).toBeInTheDocument();
    expect(screen.getByText('QUICK WINS')).toBeInTheDocument();
    expect(screen.getByText('IMPROVEMENT OPPORTUNITIES')).toBeInTheDocument();
    expect(screen.getByText('PERFORMING WELL')).toBeInTheDocument();
  });

  test('calculates critical courses correctly', () => {
    render(<PriorityDashboard courses={mockCourses} />);
    
    // Should show 2 courses with critical issues (courses 1 and 3)
    const criticalCard = screen.getByText('URGENT ACTIONS').closest('div');
    expect(criticalCard).toHaveTextContent('2');
  });

  test('calculates quick wins correctly', () => {
    render(<PriorityDashboard courses={mockCourses} />);
    
    // Course 2 (rating 4.8, 0 critical) and Course 3 (rating 4.2, 1 critical) are quick wins
    const quickWinCard = screen.getByText('QUICK WINS').closest('div');
    expect(quickWinCard).toHaveTextContent('2');
  });

  test('handles action click', () => {
    const mockOnActionClick = jest.fn();
    render(<PriorityDashboard courses={mockCourses} onActionClick={mockOnActionClick} />);
    
    const criticalCard = screen.getByText('URGENT ACTIONS').closest('div');
    if (criticalCard) {
      fireEvent.click(criticalCard);
      expect(mockOnActionClick).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'critical',
          count: 2,
          courses: expect.arrayContaining([
            expect.objectContaining({ id: '1' }),
            expect.objectContaining({ id: '3' })
          ])
        })
      );
    }
  });

  test('shows course examples in action cards', () => {
    render(<PriorityDashboard courses={mockCourses} />);
    
    // Should show "Next: Test Course..." for cards with courses (multiple instances)
    expect(screen.getAllByText(/Next: Test Course/)).toHaveLength(4); // One for each action type
  });

  test('displays priority badges correctly', () => {
    render(<PriorityDashboard courses={mockCourses} />);
    
    // Priority badges have space in them: "high Priority", "medium Priority", etc.
    expect(screen.getByText(/high\s+Priority/)).toBeInTheDocument();
    expect(screen.getAllByText(/medium\s+Priority/)).toHaveLength(2);
    expect(screen.getByText(/low\s+Priority/)).toBeInTheDocument();
  });
}); 