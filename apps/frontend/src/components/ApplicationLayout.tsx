import React from 'react';
import { HeaderNav } from './HeaderNav';
import { ScoringControls } from './ScoringControls';
import { DataSourceStatusComponent } from './DataSourceStatus';
import { ScoringWeights, DataSourceStatus } from '../types';

interface ApplicationLayoutProps {
  isDarkMode: boolean;
  onToggleTheme: () => void;
  children: React.ReactNode;
  // Scoring weights props
  scoringWeights: ScoringWeights;
  onWeightsChange: (weights: ScoringWeights) => void;
  onRecompute: () => void;
  onReset: () => void;
  isRecomputing: boolean;
  // Data source props
  dataSourceStatus: DataSourceStatus;
  onSync: (source: 'canvas' | 'zoho') => void;
  isSyncing: { canvas: boolean; zoho: boolean };
}

export const ApplicationLayout: React.FC<ApplicationLayoutProps> = ({
  isDarkMode,
  onToggleTheme,
  children,
  scoringWeights,
  onWeightsChange,
  onRecompute,
  onReset,
  isRecomputing,
  dataSourceStatus,
  onSync,
  isSyncing
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
            <div className="space-y-6">
              <ScoringControls
                weights={scoringWeights}
                onWeightsChange={onWeightsChange}
                onRecompute={onRecompute}
                onReset={onReset}
                isRecomputing={isRecomputing}
              />
              
              <DataSourceStatusComponent
                status={dataSourceStatus}
                onSync={onSync}
                isSyncing={isSyncing.canvas || isSyncing.zoho}
              />
            </div>
          </div>
        </div>
        
        {/* Right Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
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