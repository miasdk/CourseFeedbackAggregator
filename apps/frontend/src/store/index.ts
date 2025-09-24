/**
 * Store exports and initialization
 */

export { useCourseStore } from './courseStore';
export { useFeedbackStore } from './feedbackStore';
export { usePriorityStore } from './priorityStore';
export { useAppStore } from './appStore';

// Store initialization helper
export const initializeStores = async () => {
  // Initialize app connections on startup
  const appStore = useAppStore.getState();
  await appStore.checkConnections();

  // Start live updates if enabled
  if (appStore.config.features.realTimeUpdates) {
    appStore.startLiveUpdates();
  }

  // Fetch initial data
  const courseStore = useCourseStore.getState();
  const priorityStore = usePriorityStore.getState();
  const feedbackStore = useFeedbackStore.getState();

  try {
    await Promise.all([
      courseStore.fetchCourses(),
      priorityStore.fetchRecommendations(),
      priorityStore.fetchScoringWeights(),
      feedbackStore.fetchRecentFeedback(),
      feedbackStore.fetchFeedbackStats(),
    ]);
  } catch (error) {
    appStore.handleError(error as Error, 'Initial data loading');
  }
};

// Store cleanup helper
export const cleanupStores = () => {
  const appStore = useAppStore.getState();
  appStore.stopLiveUpdates();
};