/**
 * Course state management with Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Course,
  CourseDetail,
  CourseFilter,
  CourseSortOption,
  LoadingState
} from '../shared/types';
import { courseApi } from '../services/api/courses';

interface CourseState {
  // Data
  courses: Course[];
  selectedCourse: CourseDetail | null;

  // UI State
  loading: LoadingState;
  error: string | null;
  filters: CourseFilter;
  sortOption: CourseSortOption;
  searchTerm: string;

  // Pagination
  currentPage: number;
  pageSize: number;
  totalCount: number;

  // Actions
  fetchCourses: () => Promise<void>;
  fetchCourseDetail: (courseId: string) => Promise<void>;
  updateFilters: (filters: Partial<CourseFilter>) => void;
  updateSort: (sort: CourseSortOption) => void;
  setSearchTerm: (term: string) => void;
  setPage: (page: number) => void;
  clearError: () => void;
  clearSelectedCourse: () => void;

  // Computed values
  filteredCourses: Course[];
}

export const useCourseStore = create<CourseState>()(
  devtools(
    (set, get) => ({
      // Initial state
      courses: [],
      selectedCourse: null,
      loading: 'idle',
      error: null,
      filters: {},
      sortOption: { field: 'courseName', direction: 'asc' },
      searchTerm: '',
      currentPage: 1,
      pageSize: 20,
      totalCount: 0,

      // Actions
      fetchCourses: async () => {
        set({ loading: 'loading', error: null });

        try {
          const { filters } = get();
          const response = await courseApi.getCourses(filters);

          if (response) {
            set({
              courses: response.courses,
              totalCount: response.total,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch courses',
          });
        }
      },

      fetchCourseDetail: async (courseId: string) => {
        set({ loading: 'loading', error: null });

        try {
          const courseDetail = await courseApi.getCourseDetail(courseId);

          if (courseDetail) {
            set({
              selectedCourse: courseDetail,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch course details',
          });
        }
      },

      updateFilters: (newFilters: Partial<CourseFilter>) => {
        const { filters, fetchCourses } = get();
        const updatedFilters = { ...filters, ...newFilters };

        set({
          filters: updatedFilters,
          currentPage: 1, // Reset to first page when filters change
        });

        fetchCourses();
      },

      updateSort: (sort: CourseSortOption) => {
        set({ sortOption: sort });
        get().fetchCourses();
      },

      setSearchTerm: (term: string) => {
        const { updateFilters } = get();
        set({ searchTerm: term });

        // Debounced search - update filters after user stops typing
        updateFilters({ searchTerm: term });
      },

      setPage: (page: number) => {
        set({ currentPage: page });
        get().fetchCourses();
      },

      clearError: () => {
        set({ error: null });
      },

      clearSelectedCourse: () => {
        set({ selectedCourse: null });
      },

      // Computed values
      get filteredCourses() {
        const { courses, searchTerm, sortOption } = get();

        let filtered = [...courses];

        // Apply search filter if present
        if (searchTerm) {
          const term = searchTerm.toLowerCase();
          filtered = filtered.filter(course =>
            course.courseName.toLowerCase().includes(term) ||
            course.department.toLowerCase().includes(term) ||
            course.instructorName.toLowerCase().includes(term)
          );
        }

        // Apply sorting
        filtered.sort((a, b) => {
          const { field, direction } = sortOption;
          let aValue = a[field] as any;
          let bValue = b[field] as any;

          // Handle string vs number sorting
          if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
          }

          if (direction === 'desc') {
            [aValue, bValue] = [bValue, aValue];
          }

          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        });

        return filtered;
      },
    }),
    {
      name: 'course-store',
    }
  )
);