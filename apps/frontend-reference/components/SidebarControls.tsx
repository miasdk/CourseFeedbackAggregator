/**
 * Sidebar Controls Component
 * 
 * Professional sidebar with organized controls for scoring weights,
 * data source management, and system statistics
 */

import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { ScoringControls } from "./ScoringControls";
import { DataSourceStatus } from "./DataSourceStatus";
import { Settings } from "lucide-react";
import { ScoringWeights, DataSourceStatus as DataSourceStatusType } from "../types";

interface SidebarControlsProps {
  scoringWeights: ScoringWeights;
  onWeightsChange: (weights: ScoringWeights) => void;
  onRecompute: () => void;
  onReset: () => void;
  isRecomputing: boolean;
  dataSourceStatus: DataSourceStatusType;
  onSync: (source: 'canvas' | 'zoho') => void;
  isSyncing: { canvas: boolean; zoho: boolean };
  onSettingsClick?: () => void;
}

/**
 * Professional sidebar with clean organization and visual hierarchy
 * Provides essential controls for the dashboard functionality
 */
export function SidebarControls({
  scoringWeights,
  onWeightsChange,
  onRecompute,
  onReset,
  isRecomputing,
  dataSourceStatus,
  onSync,
  isSyncing,
  onSettingsClick
}: SidebarControlsProps) {
  return (
    <div className="space-y-6">
      {/* Scoring Controls */}
      <ScoringControls
        weights={scoringWeights}
        onWeightsChange={onWeightsChange}
        onRecompute={onRecompute}
        onReset={onReset}
        isRecomputing={isRecomputing}
      />
      
      {/* Data Source Status */}
      <DataSourceStatus
        status={dataSourceStatus}
        onSync={onSync}
        isSyncing={isSyncing}
      />
      
      {/* System Settings */}
      <Card>
        <CardContent className="p-4">
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full"
            onClick={onSettingsClick}
          >
            <Settings className="h-4 w-4 mr-2" />
            System Settings
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}