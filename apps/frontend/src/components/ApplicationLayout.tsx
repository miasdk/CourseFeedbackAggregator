import React from 'react';
import { Navbar } from './Navbar';
import { HeaderNav } from './HeaderNav';
import { ScoringControls } from './ScoringControls';
import { DataSourceStatusComponent } from './DataSourceStatus';
import { ScoringWeights, DataSourceStatus } from '../types';

interface ApplicationLayoutProps {
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
    <div className="h-screen w-full flex flex-col bg-gray-50">
      {/* Navbar - Fixed at Top with White Background */}
      <div className="w-full flex-shrink-0 z-50">
        <Navbar />
      </div>
      
      {/* Header Nav - Below Navbar */}
      <div className="w-full border-b bg-white flex-shrink-0 shadow-sm">
        <HeaderNav />
      </div>
      
      {/* Main Layout Area - Sidebar Left, Content Right */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar - Fixed Width with Better Styling */}
        <div className="w-80 bg-white border-r border-gray-200 flex-shrink-0 overflow-y-auto">
          <div className="p-6 space-y-6">
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