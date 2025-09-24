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
      {/* Stats Cards with improved design */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Recommendations
            </CardTitle>
            <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{displayCount}</div>
            {hasActiveFilters && (
              <p className="text-xs text-gray-500 mt-1">
                Filtered from {totalRecommendations} total
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Critical Issues
            </CardTitle>
            <div className="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center">
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{criticalIssues}</div>
            <p className="text-xs text-gray-500 mt-1">
              Require immediate attention
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Validation Rate
            </CardTitle>
            <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
              <CheckCircle className="h-4 w-4 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{validationRate}%</div>
            <p className="text-xs text-gray-500 mt-1">
              Recommendations validated
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Average Priority Score
            </CardTitle>
            <div className="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center">
              <Clock className="h-4 w-4 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{averagePriorityScore.toFixed(1)}</div>
            <p className="text-xs text-gray-500 mt-1">
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