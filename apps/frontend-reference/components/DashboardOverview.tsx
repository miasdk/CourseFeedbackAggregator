/**
 * Dashboard Overview Component
 * 
 * Displays key metrics and statistics about course recommendations
 * in a clean, professional row layout above the main content area
 */

import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";

interface DashboardOverviewProps {
  totalRecommendations: number;
  filteredCount: number;
  criticalIssues: number;
  validationRate: number;
  averagePriorityScore: number;
  hasActiveFilters: boolean;
}

/**
 * Professional dashboard overview with key metrics
 * Displays statistics in a clean grid layout
 */
export function DashboardOverview({
  totalRecommendations,
  filteredCount,
  criticalIssues,
  validationRate,
  averagePriorityScore,
  hasActiveFilters
}: DashboardOverviewProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      {/* Total Recommendations */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">
              {hasActiveFilters ? 'Filtered' : 'Total'} Recommendations
            </div>
            <div className="text-2xl font-semibold">
              {hasActiveFilters ? filteredCount : totalRecommendations}
            </div>
            {hasActiveFilters && (
              <div className="text-xs text-muted-foreground">
                of {totalRecommendations} total
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Critical Issues */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Critical Issues</div>
            <div className="text-2xl font-semibold">
              {criticalIssues}
            </div>
            <div className="text-xs text-muted-foreground">
              Show stoppers
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation Rate */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Validation Rate</div>
            <div className="text-2xl font-semibold">
              {validationRate}%
            </div>
            <div className="text-xs text-muted-foreground">
              Reviewed & validated
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Average Priority Score */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-1">
            <div className="text-sm text-muted-foreground">Average Score</div>
            <div className="text-2xl font-semibold">
              {averagePriorityScore}/5
            </div>
            <div className="text-xs text-muted-foreground">
              Priority rating
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}