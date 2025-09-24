/**
 * Feedback and survey response state management with Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  SurveyResponse,
  FeedbackSection,
  FeedbackStats,
  FeedbackFilter,
  ShowstopperIssue,
  LoadingState
} from '../shared/types';
import { feedbackApi } from '../services/api/feedback';

interface FeedbackState {
  // Data
  feedbackResponses: SurveyResponse[];
  selectedResponse: SurveyResponse | null;
  feedbackStats: FeedbackStats | null;
  showstoppers: ShowstopperIssue[];
  recentFeedback: SurveyResponse[];

  // UI State
  loading: LoadingState;
  error: string | null;
  filters: FeedbackFilter;

  // Pagination
  currentPage: number;
  pageSize: number;
  totalCount: number;
  hasMore: boolean;

  // Actions
  fetchCourseFeedback: (courseId: string) => Promise<void>;
  fetchFeedbackStats: () => Promise<void>;
  fetchShowstoppers: () => Promise<void>;
  fetchRecentFeedback: (limit?: number) => Promise<void>;
  fetchSurveyResponse: (responseId: string) => Promise<void>;
  resolveShowstopper: (feedbackId: string, resolution: { resolved: boolean; notes?: string }) => Promise<void>;

  // Filter and pagination
  updateFilters: (filters: Partial<FeedbackFilter>) => void;
  setPage: (page: number) => void;
  loadMoreFeedback: () => Promise<void>;

  // UI Actions
  setSelectedResponse: (response: SurveyResponse | null) => void;
  clearError: () => void;

  // Computed values
  filteredShowstoppers: ShowstopperIssue[];
}

export const useFeedbackStore = create<FeedbackState>()(
  devtools(
    (set, get) => ({
      // Initial state
      feedbackResponses: [],
      selectedResponse: null,
      feedbackStats: null,
      showstoppers: [],
      recentFeedback: [],
      loading: 'idle',
      error: null,
      filters: {},
      currentPage: 1,
      pageSize: 20,
      totalCount: 0,
      hasMore: false,

      // Actions
      fetchCourseFeedback: async (courseId: string) => {
        set({ loading: 'loading', error: null });

        try {
          const { filters, currentPage, pageSize } = get();

          const response = await feedbackApi.getCourseFeedback(courseId, {
            ...filters,
            limit: pageSize,
            offset: (currentPage - 1) * pageSize,
          });

          if (response) {
            set({
              feedbackResponses: currentPage === 1
                ? response.feedback
                : [...get().feedbackResponses, ...response.feedback],
              totalCount: response.total,
              hasMore: response.hasMore,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch feedback',
          });
        }
      },

      fetchFeedbackStats: async () => {
        try {
          const { filters } = get();
          const stats = await feedbackApi.getFeedbackStats({
            courseId: filters.courseId?.toString(),
            dateRange: filters.dateRange ?
              `${filters.dateRange.start}_${filters.dateRange.end}` : undefined,
          });

          if (stats) {
            set({ feedbackStats: stats });
          }
        } catch (error) {
          console.error('Failed to fetch feedback stats:', error);
        }
      },

      fetchShowstoppers: async () => {
        try {
          const response = await feedbackApi.getShowstoppers({
            limit: 100,
            resolved: false,
          });

          if (response) {
            set({ showstoppers: response.showstoppers as ShowstopperIssue[] });
          }
        } catch (error) {
          console.error('Failed to fetch showstoppers:', error);
        }
      },

      fetchRecentFeedback: async (limit = 10) => {
        try {
          const response = await feedbackApi.getRecentFeedback(limit);

          if (response) {
            set({ recentFeedback: response.feedback });
          }
        } catch (error) {
          console.error('Failed to fetch recent feedback:', error);
        }
      },

      fetchSurveyResponse: async (responseId: string) => {
        set({ loading: 'loading', error: null });

        try {
          const response = await feedbackApi.getSurveyResponse(responseId);

          if (response) {
            set({
              selectedResponse: response,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch survey response',
          });
        }
      },

      resolveShowstopper: async (feedbackId: string, resolution: { resolved: boolean; notes?: string }) => {
        try {
          await feedbackApi.resolveShowstopper(feedbackId, resolution);

          // Update the showstopper in the local state
          set(state => ({
            showstoppers: state.showstoppers.map(issue =>
              issue.id === feedbackId
                ? {
                    ...issue,
                    status: resolution.resolved ? 'resolved' : 'open',
                    resolution: resolution.resolved ? {
                      resolvedAt: new Date().toISOString(),
                      resolvedBy: 'current_user', // TODO: Get from auth context
                      notes: resolution.notes || '',
                      actions: [],
                    } : undefined,
                  }
                : issue
            ),
          }));
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to resolve showstopper',
          });
        }
      },

      // Filter and pagination
      updateFilters: (newFilters: Partial<FeedbackFilter>) => {
        set(state => ({
          filters: { ...state.filters, ...newFilters },
          currentPage: 1, // Reset to first page
          feedbackResponses: [], // Clear existing responses
        }));
      },

      setPage: (page: number) => {
        set({ currentPage: page });
      },

      loadMoreFeedback: async () => {
        const { hasMore, loading, currentPage } = get();

        if (!hasMore || loading === 'loading') return;

        set({ currentPage: currentPage + 1 });

        // The actual loading happens in fetchCourseFeedback
        // This just sets up pagination for the next fetch
      },

      // UI Actions
      setSelectedResponse: (response: SurveyResponse | null) => {
        set({ selectedResponse: response });
      },

      clearError: () => {
        set({ error: null });
      },

      // Computed values
      get filteredShowstoppers() {
        const { showstoppers, filters } = get();

        let filtered = [...showstoppers];

        if (filters.courseId) {
          filtered = filtered.filter(issue =>
            issue.affectedCourses.some(courseId =>
              courseId === filters.courseId?.toString()
            )
          );
        }

        if (filters.ratingRange) {
          const [min, max] = filters.ratingRange;
          filtered = filtered.filter(issue =>
            issue.rating >= min && issue.rating <= max
          );
        }

        if (filters.searchTerm) {
          const term = filters.searchTerm.toLowerCase();
          filtered = filtered.filter(issue =>
            issue.positiveFeedback.toLowerCase().includes(term) ||
            issue.improvementSuggestions.toLowerCase().includes(term) ||
            issue.sectionName.toLowerCase().includes(term)
          );
        }

        return filtered;
      },
    }),
    {
      name: 'feedback-store',
    }
  )
);