import { useState, useCallback } from 'react';
import { Toaster } from 'sonner';
import { ApplicationLayout } from './components/ApplicationLayout';
import { RecommendationsList } from './components/RecommendationsList';
import { DashboardOverview } from './components/DashboardOverview';
import MockModeIndicator from './components/MockModeIndicator';
import { useRecommendations } from './hooks/useRecommendations';
import { useDataSync } from './hooks/useDataSync';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const {
    recommendations,
    scoringWeights,
    isLoading,
    isRecomputing,
    error,
    stats,
    updateWeights,
    recomputeScores,
    resetWeights,
    validateRecommendation
  } = useRecommendations();

  const {
    dataSourceStatus,
    isSyncing,
    syncDataSource
  } = useDataSync();

  const handleToggleTheme = useCallback(() => {
    setIsDarkMode(prev => !prev);
  }, []);

  const handleViewRecommendationDetails = useCallback((recommendation: any) => {
    console.log('View details:', recommendation);
  }, []);

  const handleValidateRecommendation = useCallback((recommendation: any) => {
    validateRecommendation(recommendation, 'Validated via dashboard');
  }, [validateRecommendation]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-muted-foreground">Loading course feedback data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <h2 className="text-xl font-semibold">Connection Error</h2>
          <p className="text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full flex-col bg-background text-foreground">
      <ApplicationLayout
        isDarkMode={isDarkMode}
        onToggleTheme={handleToggleTheme}
        scoringWeights={scoringWeights}
        onWeightsChange={updateWeights}
        onRecompute={recomputeScores}
        onReset={resetWeights}
        isRecomputing={isRecomputing}
        dataSourceStatus={dataSourceStatus}
        onSync={syncDataSource}
        isSyncing={isSyncing}
      >
        {/* Dashboard Overview */}
        <DashboardOverview
          totalRecommendations={stats.total}
          criticalIssues={stats.showStoppers}
          validationRate={stats.total > 0 ? Math.round((stats.validated / stats.total) * 100) : 0}
          averagePriorityScore={stats.averageScore}
        />

        {/* Recommendations Content */}
        <RecommendationsList
          recommendations={recommendations}
          onViewDetails={handleViewRecommendationDetails}
          onValidate={handleValidateRecommendation}
        />
      </ApplicationLayout>

      {/* Mock Mode Indicator */}
      <MockModeIndicator />

      {/* Global Toast Notifications */}
      <Toaster 
        position="bottom-right"
        richColors
        closeButton
        expand
        visibleToasts={5}
      />
    </div>
  );
}

export default App;