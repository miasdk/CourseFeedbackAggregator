import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import SmartFilters, { SmartFiltersProps } from '../SmartFilters';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <div>{children}</div>,
}));

describe('SmartFilters', () => {
  const defaultProps: SmartFiltersProps = {
    selectedIssueCategories: [],
    selectedPriorityLevels: [],
    selectedActionStatus: [],
    showOnlyWithActions: false,
    onIssueCategoryToggle: jest.fn(),
    onPriorityLevelToggle: jest.fn(),
    onActionStatusToggle: jest.fn(),
    onToggleShowOnlyWithActions: jest.fn(),
    onClearFilters: jest.fn(),
    filteredCount: 10,
    totalCount: 25,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders smart filters component', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText('Smart Filters')).toBeInTheDocument();
    expect(screen.getByText('Showing 10 of 25 courses')).toBeInTheDocument();
  });

  test('displays all issue categories', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText('Technical Issues')).toBeInTheDocument();
    expect(screen.getByText('Content Issues')).toBeInTheDocument();
    expect(screen.getByText('Instructional Issues')).toBeInTheDocument();
    expect(screen.getByText('UX Issues')).toBeInTheDocument();
    expect(screen.getByText('Engagement Issues')).toBeInTheDocument();
  });

  test('displays all priority levels', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText('Urgent')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  test('displays action status options', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText('Pending Actions')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  test('calls onIssueCategoryToggle when issue category is clicked', () => {
    render(<SmartFilters {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Technical Issues'));
    expect(defaultProps.onIssueCategoryToggle).toHaveBeenCalledWith('technical');
  });

  test('calls onPriorityLevelToggle when priority level is clicked', () => {
    render(<SmartFilters {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Urgent'));
    expect(defaultProps.onPriorityLevelToggle).toHaveBeenCalledWith('urgent');
  });

  test('calls onActionStatusToggle when action status is clicked', () => {
    render(<SmartFilters {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Pending Actions'));
    expect(defaultProps.onActionStatusToggle).toHaveBeenCalledWith('pending');
  });

  test('calls onToggleShowOnlyWithActions when quick action is clicked', () => {
    render(<SmartFilters {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Courses with Action Items'));
    expect(defaultProps.onToggleShowOnlyWithActions).toHaveBeenCalled();
  });

  test('shows active filters in selected state', () => {
    const propsWithSelections: SmartFiltersProps = {
      ...defaultProps,
      selectedIssueCategories: ['technical'],
      selectedPriorityLevels: ['urgent'],
      selectedActionStatus: ['pending'],
      showOnlyWithActions: true,
    };
    
    render(<SmartFilters {...propsWithSelections} />);
    
    // Check that selected items have different styling
    const technicalButton = screen.getByText('Technical Issues').closest('button');
    const urgentButton = screen.getByText('Urgent').closest('button');
    const pendingButton = screen.getByText('Pending Actions').closest('button');
    const actionItemsButton = screen.getByText('Courses with Action Items').closest('button');
    
    expect(technicalButton).toHaveClass('border-red-200', 'bg-red-50');
    expect(urgentButton).toHaveClass('border-red-200', 'bg-red-50');
    expect(pendingButton).toHaveClass('border-gray-200', 'bg-gray-50');
    expect(actionItemsButton).toHaveClass('border-blue-200', 'bg-blue-50');
  });

  test('shows clear all button when filters are active', () => {
    const propsWithSelections: SmartFiltersProps = {
      ...defaultProps,
      selectedIssueCategories: ['technical'],
    };
    
    render(<SmartFilters {...propsWithSelections} />);
    
    expect(screen.getByText('Clear All')).toBeInTheDocument();
  });

  test('hides clear all button when no filters are active', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.queryByText('Clear All')).not.toBeInTheDocument();
  });

  test('calls onClearFilters when clear all button is clicked', () => {
    const propsWithSelections: SmartFiltersProps = {
      ...defaultProps,
      selectedIssueCategories: ['technical'],
    };
    
    render(<SmartFilters {...propsWithSelections} />);
    
    fireEvent.click(screen.getByText('Clear All'));
    expect(defaultProps.onClearFilters).toHaveBeenCalled();
  });

  test('displays filter summary correctly', () => {
    const propsWithSelections: SmartFiltersProps = {
      ...defaultProps,
      selectedIssueCategories: ['technical', 'content'],
      selectedPriorityLevels: ['urgent'],
      selectedActionStatus: ['pending', 'in-progress'],
    };
    
    render(<SmartFilters {...propsWithSelections} />);
    
    expect(screen.getByText('Categories: 2')).toBeInTheDocument();
    expect(screen.getByText('Priority: 1')).toBeInTheDocument();
    expect(screen.getByText('Status: 2')).toBeInTheDocument();
  });

  test('displays "All" when no filters are selected in summary', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText('Categories: All')).toBeInTheDocument();
    expect(screen.getByText('Priority: All')).toBeInTheDocument();
    expect(screen.getByText('Status: All')).toBeInTheDocument();
  });

  test('handles multiple issue categories selection', () => {
    const propsWithMultipleSelections: SmartFiltersProps = {
      ...defaultProps,
      selectedIssueCategories: ['technical', 'content', 'instructional'],
    };
    
    render(<SmartFilters {...propsWithMultipleSelections} />);
    
    // All three selected categories should have selected styling
    const technicalButton = screen.getByText('Technical Issues').closest('button');
    const contentButton = screen.getByText('Content Issues').closest('button');
    const instructionalButton = screen.getByText('Instructional Issues').closest('button');
    
    expect(technicalButton).toHaveClass('border-red-200', 'bg-red-50');
    expect(contentButton).toHaveClass('border-orange-200', 'bg-orange-50');
    expect(instructionalButton).toHaveClass('border-yellow-200', 'bg-yellow-50');
  });

  test('updates course count display correctly', () => {
    const { rerender } = render(<SmartFilters {...defaultProps} />);
    expect(screen.getByText('Showing 10 of 25 courses')).toBeInTheDocument();
    
    rerender(<SmartFilters {...defaultProps} filteredCount={5} totalCount={30} />);
    expect(screen.getByText('Showing 5 of 30 courses')).toBeInTheDocument();
  });

  test('renders issue category descriptions', () => {
    render(<SmartFilters {...defaultProps} />);
    
    expect(screen.getByText(/Audio\/video problems, platform glitches/)).toBeInTheDocument();
    expect(screen.getByText(/Outdated examples, missing materials/)).toBeInTheDocument();
    expect(screen.getByText(/Unclear explanations, pacing problems/)).toBeInTheDocument();
    expect(screen.getByText(/Navigation problems, accessibility issues/)).toBeInTheDocument();
    expect(screen.getByText(/Boring content, lack of interaction/)).toBeInTheDocument();
  });

  test('accessible button structure', () => {
    render(<SmartFilters {...defaultProps} />);
    
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
    
    // Check that important buttons have accessible text
    expect(screen.getByRole('button', { name: /Technical Issues/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Urgent/ })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Courses with Action Items/ })).toBeInTheDocument();
  });
}); 