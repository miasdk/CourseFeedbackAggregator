/**
 * Priority and recommendation state management with Zustand
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Recommendation,
  CoursePriority,
  ScoringWeights,
  WeightConfiguration,
  PriorityExplanation,
  LoadingState
} from '../shared/types';
import { priorityApi } from '../services/api/priorities';

interface PriorityState {
  // Data
  recommendations: Recommendation[];
  priorities: CoursePriority[];
  scoringWeights: ScoringWeights | null;
  weightConfigurations: WeightConfiguration[];
  explanations: Record<string, PriorityExplanation>; // courseId -> explanation

  // UI State
  loading: LoadingState;
  weightsLoading: LoadingState;
  error: string | null;
  selectedRecommendation: Recommendation | null;

  // Settings
  minScore: number;
  maxRecommendations: number;
  includeExplanations: boolean;

  // Actions
  fetchRecommendations: () => Promise<void>;
  fetchPriorities: () => Promise<void>;
  fetchScoringWeights: () => Promise<void>;
  updateWeights: (weights: Partial<ScoringWeights>) => Promise<void>;
  recalculatePriorities: (weights?: Partial<ScoringWeights>) => Promise<void>;
  fetchExplanation: (courseId: string) => Promise<void>;
  saveWeightConfiguration: (config: { name: string; description?: string }) => Promise<void>;
  loadWeightConfiguration: (configId: string) => Promise<void>;

  // UI Actions
  setSelectedRecommendation: (recommendation: Recommendation | null) => void;
  updateSettings: (settings: Partial<{
    minScore: number;
    maxRecommendations: number;
    includeExplanations: boolean;
  }>) => void;
  clearError: () => void;
}

export const usePriorityStore = create<PriorityState>()(
  devtools(
    (set, get) => ({
      // Initial state
      recommendations: [],
      priorities: [],
      scoringWeights: null,
      weightConfigurations: [],
      explanations: {},
      loading: 'idle',
      weightsLoading: 'idle',
      error: null,
      selectedRecommendation: null,
      minScore: 0,
      maxRecommendations: 50,
      includeExplanations: true,

      // Actions
      fetchRecommendations: async () => {
        set({ loading: 'loading', error: null });

        try {
          const { minScore, maxRecommendations, includeExplanations } = get();

          const response = await priorityApi.getRecommendations({
            minScore,
            limit: maxRecommendations,
            includeExplanations,
          });

          if (response) {
            set({
              recommendations: response.recommendations,
              scoringWeights: response.weights,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch recommendations',
          });
        }
      },

      fetchPriorities: async () => {
        set({ loading: 'loading', error: null });

        try {
          const response = await priorityApi.getCoursePriorities({
            sortBy: 'priority',
            order: 'desc',
          });

          if (response) {
            set({
              priorities: response.priorities,
              loading: 'success',
            });
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch priorities',
          });
        }
      },

      fetchScoringWeights: async () => {
        set({ weightsLoading: 'loading' });

        try {
          const weights = await priorityApi.getScoringWeights();
          const configurations = await priorityApi.getWeightConfigurations();

          if (weights && configurations) {
            set({
              scoringWeights: weights,
              weightConfigurations: configurations.configurations,
              weightsLoading: 'success',
            });
          }
        } catch (error) {
          set({
            weightsLoading: 'error',
            error: error instanceof Error ? error.message : 'Failed to fetch scoring weights',
          });
        }
      },

      updateWeights: async (weights: Partial<ScoringWeights>) => {
        set({ weightsLoading: 'loading' });

        try {
          const response = await priorityApi.updateScoringWeights(weights);

          if (response) {
            set({
              scoringWeights: response.weights,
              weightsLoading: 'success',
            });

            // Automatically refetch recommendations with new weights
            await get().fetchRecommendations();
          }
        } catch (error) {
          set({
            weightsLoading: 'error',
            error: error instanceof Error ? error.message : 'Failed to update weights',
          });
        }
      },

      recalculatePriorities: async (weights?: Partial<ScoringWeights>) => {
        set({ loading: 'loading' });

        try {
          const response = await priorityApi.recalculatePriorities(weights);

          if (response) {
            set({
              priorities: response.priorities,
              loading: 'success',
            });

            // Also refresh recommendations
            await get().fetchRecommendations();
          }
        } catch (error) {
          set({
            loading: 'error',
            error: error instanceof Error ? error.message : 'Failed to recalculate priorities',
          });
        }
      },

      fetchExplanation: async (courseId: string) => {
        try {
          const explanation = await priorityApi.getPriorityExplanation(courseId);

          if (explanation) {
            set(state => ({
              explanations: {
                ...state.explanations,
                [courseId]: explanation,
              },
            }));
          }
        } catch (error) {
          console.error('Failed to fetch explanation:', error);
        }
      },

      saveWeightConfiguration: async (config: { name: string; description?: string }) => {
        const { scoringWeights } = get();

        if (!scoringWeights) {
          set({ error: 'No weights to save' });
          return;
        }

        try {
          await priorityApi.saveWeightConfiguration({
            ...config,
            weights: scoringWeights,
          });

          // Refresh configurations list
          await get().fetchScoringWeights();
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to save configuration',
          });
        }
      },

      loadWeightConfiguration: async (configId: string) => {
        const { weightConfigurations } = get();
        const config = weightConfigurations.find(c => c.id === configId);

        if (!config) {
          set({ error: 'Configuration not found' });
          return;
        }

        // Load the weights from the configuration
        await get().updateWeights(config.weights);
      },

      // UI Actions
      setSelectedRecommendation: (recommendation: Recommendation | null) => {
        set({ selectedRecommendation: recommendation });
      },

      updateSettings: (settings) => {
        set(state => ({
          ...state,
          ...settings,
        }));

        // Re-fetch recommendations if settings changed
        get().fetchRecommendations();
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'priority-store',
    }
  )
);