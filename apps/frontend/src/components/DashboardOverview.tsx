import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { TrendingUp, AlertTriangle, CheckCircle, Clock } from "lucide-react";

interface DashboardOverviewProps {
  totalRecommendations: number;
  filteredCount?: number;
  criticalIssues: number;
  validationRate: number;
  averagePriorityScore: number;
  hasActiveFilters?: boolean;
}

export function DashboardOverview({
  totalRecommendations,
  filteredCount,
  criticalIssues,
  validationRate,
  averagePriorityScore,
  hasActiveFilters = false
}: DashboardOverviewProps) {
  const displayCount = hasActiveFilters && filteredCount !== undefined ? filteredCount : totalRecommendations;

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Recommendations
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{displayCount}</div>
            {hasActiveFilters && (
              <p className="text-xs text-muted-foreground">
                Filtered from {totalRecommendations} total
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Critical Issues
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{criticalIssues}</div>
            <p className="text-xs text-muted-foreground">
              Require immediate attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Validation Rate
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{validationRate}%</div>
            <p className="text-xs text-muted-foreground">
              Recommendations validated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Average Priority Score
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averagePriorityScore.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Out of 10.0 maximum
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Active Filters Indicator */}
      {hasActiveFilters && (
        <div className="flex items-center gap-2">
          <Badge variant="secondary">
            Filters Active
          </Badge>
          <span className="text-sm text-muted-foreground">
            Showing {displayCount} of {totalRecommendations} recommendations
          </span>
        </div>
      )}
    </div>
  );
}