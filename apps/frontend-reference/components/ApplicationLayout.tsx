/**
 * Application Layout Component - Rebuilt from Scratch
 * 
 * Clean layout structure with:
 * - Full-width header nav at top
 * - Horizontal layout below with sidebar left and content right
 * - Proper spacing and no overlaps
 */

import React from 'react';
import { HeaderNav } from './HeaderNav';
import { SidebarControls } from './SidebarControls';
import { DashboardHeader } from './DashboardHeader';
import { ScoringWeights, DataSourceStatus } from '../types';

interface ApplicationLayoutProps {
  /** Current theme state */
  isDarkMode: boolean;
  /** Theme toggle handler */
  onToggleTheme: () => void;
  /** Scoring configuration */
  scoringWeights: ScoringWeights;
  /** Scoring weights change handler */
  onWeightsChange: (weights: ScoringWeights) => void;
  /** Score recomputation handler */
  onRecompute: () => void;
  /** Weights reset handler */
  onReset: () => void;
  /** Recomputation loading state */
  isRecomputing: boolean;
  /** Data source status information */
  dataSourceStatus: DataSourceStatus;
  /** Data sync handler */
  onSync: (source: 'canvas' | 'zoho') => void;
  /** Sync loading states */
  isSyncing: { canvas: boolean; zoho: boolean };
  /** Settings panel handler */
  onSettingsClick: () => void;
  /** Search query state */
  searchQuery: string;
  /** Search query change handler */
  onSearchChange: (query: string) => void;
  /** Status filter state */
  statusFilter: string;
  /** Status filter change handler */
  onStatusFilterChange: (status: string) => void;
  /** Category filter state */
  categoryFilter: string;
  /** Category filter change handler */
  onCategoryFilterChange: (category: string) => void;
  /** Total recommendations count */
  totalRecommendations: number;
  /** Filtered recommendations count */
  filteredCount: number;
  /** Dashboard refresh handler */
  onRefresh: () => void;
  /** Refresh loading state */
  isRefreshing: boolean;
  /** Main content area */
  children: React.ReactNode;
}

/**
 * Clean application layout rebuilt from scratch
 */
export const ApplicationLayout: React.FC<ApplicationLayoutProps> = ({
  isDarkMode,
  onToggleTheme,
  scoringWeights,
  onWeightsChange,
  onRecompute,
  onReset,
  isRecomputing,
  dataSourceStatus,
  onSync,
  isSyncing,
  onSettingsClick,
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  categoryFilter,
  onCategoryFilterChange,
  totalRecommendations,
  filteredCount,
  onRefresh,
  isRefreshing,
  children
}) => {
  return (
    <div className="h-screen w-full flex flex-col bg-background">
      {/* Full Width Header Nav - Fixed at Top */}
      <div className="w-full border-b bg-background flex-shrink-0">
        <HeaderNav 
          onToggleTheme={onToggleTheme} 
          isDarkMode={isDarkMode}
        />
      </div>
      
      {/* Main Layout Area - Sidebar Left, Content Right */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar - Fixed Width */}
        <div className="w-80 border-r bg-background flex-shrink-0 overflow-y-auto">
          <div className="p-6">
            <SidebarControls
              scoringWeights={scoringWeights}
              onWeightsChange={onWeightsChange}
              onRecompute={onRecompute}
              onReset={onReset}
              isRecomputing={isRecomputing}
              dataSourceStatus={dataSourceStatus}
              onSync={onSync}
              isSyncing={isSyncing}
              onSettingsClick={onSettingsClick}
            />
          </div>
        </div>
        
        {/* Right Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          
          {/* Dashboard Header - In Content Area */}
          <div className="border-b bg-background flex-shrink-0">
            <div className="p-6">
              <DashboardHeader
                searchQuery={searchQuery}
                onSearchChange={onSearchChange}
                statusFilter={statusFilter}
                onStatusFilterChange={onStatusFilterChange}
                categoryFilter={categoryFilter}
                onCategoryFilterChange={onCategoryFilterChange}
                totalRecommendations={totalRecommendations}
                filteredCount={filteredCount}
                onRefresh={onRefresh}
                isRefreshing={isRefreshing}
              />
            </div>
          </div>
          
          {/* Main Content - Scrollable */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              {children}
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

ApplicationLayout.displayName = 'ApplicationLayout';