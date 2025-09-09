import { useState } from 'react';
import { Toaster } from 'sonner';
import { ScoringControls } from './components/ScoringControls';
import { DataSourceStatusComponent } from './components/DataSourceStatus';
import { StatsOverview } from './components/StatsOverview';
import { RecommendationCard } from './components/RecommendationCard';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Search, Filter, RefreshCw, Settings, TrendingUp, AlertTriangle } from 'lucide-react';
import { useRecommendations } from './hooks/useRecommendations';
import { useDataSync } from './hooks/useDataSync';

function App() {
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
    validateRecommendation,
    refresh
  } = useRecommendations();

  const {
    dataSourceStatus,
    isSyncing,
    isRefreshing,
    syncDataSource,
    refreshDashboard
  } = useDataSync();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Filter recommendations based on search and status
  const filteredRecommendations = recommendations.filter(rec => {
    const matchesSearch = searchQuery === '' || [
      rec.title,
      rec.description,
      rec.course_name
    ].some(field => field.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || rec.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    // Sort by show stoppers first, then priority score
    if (a.is_show_stopper && !b.is_show_stopper) return -1;
    if (!a.is_show_stopper && b.is_show_stopper) return 1;
    return b.priority_score - a.priority_score;
  });

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
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto" />
          <h2 className="text-xl font-semibold">Connection Error</h2>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={refresh}>Retry Connection</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold">Course Feedback Intelligence</h1>
                <p className="text-sm text-muted-foreground">
                  Explainable priority scoring for course improvements
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={refreshDashboard}
                disabled={isRefreshing}
              >
                {isRefreshing ? (
                  <RefreshCw className="h-4 w-4 animate-spin mr-1" />
                ) : (
                  <RefreshCw className="h-4 w-4 mr-1" />
                )}
                Refresh
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-80 border-r bg-background h-[calc(100vh-73px)] overflow-y-auto">
          <div className="p-6 space-y-6">
            <ScoringControls
              weights={scoringWeights}
              onWeightsChange={updateWeights}
              onRecompute={recomputeScores}
              onReset={resetWeights}
              isRecomputing={isRecomputing}
            />
            
            <DataSourceStatusComponent
              status={dataSourceStatus}
              onSync={syncDataSource}
              isSyncing={isSyncing}
            />
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 h-[calc(100vh-73px)] overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Stats Overview */}
            <StatsOverview
              totalRecommendations={stats.total}
              showStoppers={stats.showStoppers}
              pending={stats.pending}
              validated={stats.validated}
              averageScore={stats.averageScore}
            />

            {/* Filters */}
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center justify-between">
                  <span>Priority Recommendations</span>
                  <Badge variant="outline">
                    {filteredRecommendations.length} of {recommendations.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 mb-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search recommendations..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 pr-4 py-2 w-full border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="validated">Validated</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>

                {/* Recommendations Grid */}
                {filteredRecommendations.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Filter className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No recommendations match your current filters</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                    {filteredRecommendations.map((recommendation) => (
                      <RecommendationCard
                        key={recommendation.id}
                        recommendation={recommendation}
                        onValidate={(rec) => validateRecommendation(rec, 'Validated via dashboard')}
                      />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>

      {/* Toast notifications */}
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