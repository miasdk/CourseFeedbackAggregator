/**
 * Course Improvement Prioritization System
 * 
 * Main application component that orchestrates the course recommendation
 * dashboard for Executive Education administrators. Integrates Canvas LMS
 * and Zoho CRM data to provide prioritized improvement recommendations
 * with explainable AI scoring and validation workflows.
 * 
 * @author Course Prioritization Team
 * @version 1.0.0
 */

import { useState, useCallback, useMemo } from "react";
import { Toaster } from "./components/ui/sonner";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ApplicationLayout } from "./components/ApplicationLayout";
import { RecommendationsList } from "./components/RecommendationsList";
import { RecommendationDetails } from "./components/RecommendationDetails";
import { DashboardOverview } from "./components/DashboardOverview";
import { ValidationModal } from "./components/ValidationModal";
import { useRecommendations } from "./hooks/useRecommendations";
import { useFilters } from "./hooks/useFilters";
import { useDataSync } from "./hooks/useDataSync";
import { useTheme } from "./hooks/useTheme";
import { Recommendation } from "./types";
import { APPLICATION_METADATA, UI_CONSTANTS, SUCCESS_MESSAGES } from "./constants/applicationConstants";
import { toast } from "sonner@2.0.3";

/**
 * Interface for the main application state
 */
interface ApplicationState {
  selectedRecommendation: Recommendation | null;
  isDetailsOpen: boolean;
  validationModalOpen: boolean;
  recommendationToValidate: Recommendation | null;
}

/**
 * Main Application Component
 * 
 * Provides a comprehensive dashboard for course administrators to:
 * - View prioritized course improvement recommendations
 * - Configure scoring algorithms with tunable weights
 * - Validate recommendations with detailed explanations
 * - Monitor data source synchronization status
 * - Export reports and track validation workflows
 */
const CourseImprovementPrioritizationSystem: React.FC = () => {
  // Core application state
  const [applicationState, setApplicationState] = useState<ApplicationState>({
    selectedRecommendation: null,
    isDetailsOpen: false,
    validationModalOpen: false,
    recommendationToValidate: null
  });

  // Business logic hooks
  const recommendationManager = useRecommendations();
  const filterManager = useFilters(recommendationManager.recommendations);
  const dataSyncManager = useDataSync();
  const themeManager = useTheme();

  // Destructure for cleaner access
  const {
    recommendations,
    scoringWeights,
    setScoringWeights,
    isRecomputing,
    validateRecommendation,
    recomputeScores,
    resetWeights,
    stats: recommendationStats
  } = recommendationManager;

  const {
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    categoryFilter,
    setCategoryFilter,
    filteredRecommendations,
    clearFilters,
    hasActiveFilters
  } = filterManager;

  const {
    dataSourceStatus,
    isSyncing,
    isRefreshing,
    syncDataSource,
    refreshDashboard
  } = dataSyncManager;

  const { isDarkMode, toggleTheme } = themeManager;

  /**
   * Computed values for dashboard metrics
   */
  const dashboardMetrics = useMemo(() => ({
    totalRecommendations: recommendations.length,
    filteredCount: filteredRecommendations.length,
    criticalIssues: recommendationStats.showStoppers,
    validationRate: recommendations.length > 0 
      ? Math.round((recommendationStats.validated / recommendations.length) * 100)
      : 0,
    averagePriorityScore: recommendationStats.averageScore
  }), [recommendations.length, filteredRecommendations.length, recommendationStats]);

  /**
   * Opens the detailed view for a specific recommendation
   * 
   * @param recommendation - The recommendation to view in detail
   */
  const handleViewRecommendationDetails = useCallback((recommendation: Recommendation): void => {
    setApplicationState(prevState => ({
      ...prevState,
      selectedRecommendation: recommendation,
      isDetailsOpen: true
    }));
  }, []);

  /**
   * Opens validation modal for a recommendation
   * 
   * @param recommendation - The recommendation to validate
   */
  const handleOpenValidationModal = useCallback((recommendation: Recommendation): void => {
    setApplicationState(prevState => ({
      ...prevState,
      validationModalOpen: true,
      recommendationToValidate: recommendation
    }));
  }, []);

  /**
   * Handles validation modal completion
   * 
   * @param recommendation - The recommendation to validate
   * @param validationNotes - Validation notes from the reviewer
   */
  const handleValidationComplete = useCallback((
    recommendation: Recommendation, 
    validationNotes: string
  ): void => {
    validateRecommendation(recommendation, validationNotes);
    
    // Close validation modal
    setApplicationState(prevState => ({
      ...prevState,
      validationModalOpen: false,
      recommendationToValidate: null
    }));
  }, [validateRecommendation]);

  /**
   * Closes validation modal
   */
  const handleCloseValidationModal = useCallback((): void => {
    setApplicationState(prevState => ({
      ...prevState,
      validationModalOpen: false,
      recommendationToValidate: null
    }));
  }, []);

  /**
   * Closes the recommendation details panel
   */
  const handleCloseRecommendationDetails = useCallback((): void => {
    setApplicationState(prevState => ({
      ...prevState,
      isDetailsOpen: false,
      selectedRecommendation: null
    }));
  }, []);

  /**
   * Handles system configuration access
   * Future implementation will open settings modal
   */
  const handleSystemConfiguration = useCallback((): void => {
    toast.info("System configuration panel will be available in the next release", {
      description: "Advanced settings and preferences coming soon",
      duration: UI_CONSTANTS.TOAST_CONFIG.duration
    });
  }, []);

  /**
   * Handles theme toggle with user feedback
   */
  const handleThemeToggle = useCallback((): void => {
    toggleTheme();
  }, [toggleTheme]);

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-full flex-col bg-background text-foreground">
        {/* Application Layout with Structured Content */}
        <ApplicationLayout
          isDarkMode={isDarkMode}
          onToggleTheme={handleThemeToggle}
          scoringWeights={scoringWeights}
          onWeightsChange={setScoringWeights}
          onRecompute={recomputeScores}
          onReset={resetWeights}
          isRecomputing={isRecomputing}
          dataSourceStatus={dataSourceStatus}
          onSync={syncDataSource}
          isSyncing={isSyncing}
          onSettingsClick={handleSystemConfiguration}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          statusFilter={statusFilter}
          onStatusFilterChange={setStatusFilter}
          categoryFilter={categoryFilter}
          onCategoryFilterChange={setCategoryFilter}
          totalRecommendations={dashboardMetrics.totalRecommendations}
          filteredCount={dashboardMetrics.filteredCount}
          onRefresh={refreshDashboard}
          isRefreshing={isRefreshing}
        >
          {/* Dashboard Overview */}
          <DashboardOverview
            totalRecommendations={dashboardMetrics.totalRecommendations}
            filteredCount={dashboardMetrics.filteredCount}
            criticalIssues={dashboardMetrics.criticalIssues}
            validationRate={dashboardMetrics.validationRate}
            averagePriorityScore={dashboardMetrics.averagePriorityScore}
            hasActiveFilters={hasActiveFilters}
          />

          {/* Recommendations Content */}
          <section aria-label="Course improvement recommendations">
            <RecommendationsList
              recommendations={filteredRecommendations}
              onViewDetails={handleViewRecommendationDetails}
              onValidate={handleOpenValidationModal}
              hasActiveFilters={hasActiveFilters}
              onClearFilters={clearFilters}
            />
          </section>
        </ApplicationLayout>

        {/* Recommendation Details Modal */}
        <RecommendationDetails
          recommendation={applicationState.selectedRecommendation}
          isOpen={applicationState.isDetailsOpen}
          onClose={handleCloseRecommendationDetails}
          onValidate={handleOpenValidationModal}
          scoringWeights={scoringWeights}
        />

        {/* Validation Modal */}
        <ValidationModal
          recommendation={applicationState.recommendationToValidate}
          isOpen={applicationState.validationModalOpen}
          onClose={handleCloseValidationModal}
          onValidate={handleValidationComplete}
        />

        {/* Global Toast Notifications */}
        <Toaster 
          position={UI_CONSTANTS.TOAST_CONFIG.position}
          richColors={UI_CONSTANTS.TOAST_CONFIG.richColors}
          closeButton={UI_CONSTANTS.TOAST_CONFIG.closeButton}
          expand={UI_CONSTANTS.TOAST_CONFIG.expand}
          visibleToasts={UI_CONSTANTS.TOAST_CONFIG.visibleToasts}
        />
      </div>
    </ErrorBoundary>
  );
};

// Export with display name for debugging
CourseImprovementPrioritizationSystem.displayName = 'CourseImprovementPrioritizationSystem';

export default CourseImprovementPrioritizationSystem;