import { useState, useCallback } from 'react';
import { Toaster } from 'sonner';
import { ApplicationLayout } from './components/ApplicationLayout';
import { RecommendationsList } from './components/RecommendationsList';
import { CoursesList } from './components/CoursesList';
import { DashboardOverview } from './components/DashboardOverview';
import { AuthModal } from './components/AuthModal';
import { CommentsModal } from './components/CommentsModal';
import { Button } from './components/ui/button';
import MockModeIndicator from './components/MockModeIndicator';
import { useRecommendations } from './hooks/useRecommendations';
import { useDataSync } from './hooks/useDataSync';
import { useCourses } from './hooks/useCourses';

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [commentsModalRecommendation, setCommentsModalRecommendation] = useState<any>(null);
  const [currentView, setCurrentView] = useState<'recommendations' | 'courses'>('recommendations');
  
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

  const {
    courses,
    isLoading: isLoadingCourses,
    error: coursesError
  } = useCourses();

  const handleToggleTheme = useCallback(() => {
    setIsDarkMode(prev => !prev);
  }, []);

  const handleViewRecommendationDetails = useCallback((recommendation: any) => {
    console.log('View details:', recommendation);
  }, []);

  const handleViewComments = useCallback((recommendation: any) => {
    setCommentsModalRecommendation(recommendation);
  }, []);

  const handleValidateRecommendation = useCallback((recommendation: any) => {
    validateRecommendation(recommendation, 'Validated via dashboard');
  }, [validateRecommendation]);

  const handleSignInClick = useCallback(() => {
    setShowAuthModal(true);
  }, []);

  const handleCloseAuthModal = useCallback(() => {
    setShowAuthModal(false);
  }, []);

  const handleViewChange = useCallback((view: 'recommendations' | 'courses') => {
    setCurrentView(view);
  }, []);

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
        scoringWeights={scoringWeights}
        onWeightsChange={updateWeights}
        onRecompute={recomputeScores}
        onReset={resetWeights}
        isRecomputing={isRecomputing}
        dataSourceStatus={dataSourceStatus}
        onSync={syncDataSource}
        isSyncing={isSyncing}
      >
        {/* Dashboard Overview - only show for recommendations view */}
        {currentView === 'recommendations' && (
          <DashboardOverview
            totalRecommendations={stats.total}
            criticalIssues={stats.showStoppers}
            validationRate={stats.total > 0 ? Math.round((stats.validated / stats.total) * 100) : 0}
            averagePriorityScore={stats.averageScore}
          />
        )}

        {/* View Toggle */}
        <div className="flex items-center justify-between mb-6 mt-8">
          <div className="flex items-center rounded-lg border p-1">
            <Button
              variant={currentView === 'recommendations' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleViewChange('recommendations')}
              className="h-8"
            >
              Recommendations
            </Button>
            <Button
              variant={currentView === 'courses' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleViewChange('courses')}
              className="h-8"
            >
              All Courses
            </Button>
          </div>
        </div>

        {/* Content based on current view */}
        {currentView === 'recommendations' ? (
          <RecommendationsList
            recommendations={recommendations}
            onViewDetails={handleViewRecommendationDetails}
            onViewComments={handleViewComments}
            onValidate={handleValidateRecommendation}
          />
        ) : (
          <CoursesList 
            courses={courses}
            loading={isLoadingCourses}
          />
        )}
      </ApplicationLayout>

      {/* Auth Modal */}
      {showAuthModal && <AuthModal onClose={handleCloseAuthModal} />}
      
      {/* Comments Modal */}
      <CommentsModal 
        recommendation={commentsModalRecommendation}
        isOpen={!!commentsModalRecommendation}
        onClose={() => setCommentsModalRecommendation(null)}
      />

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