import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { RecommendationCard } from "./RecommendationCard";
import { Search } from "lucide-react";
import type { Recommendation } from "../hooks/useRecommendations";

interface RecommendationsListProps {
  recommendations: Recommendation[];
  onViewDetails: (recommendation: Recommendation) => void;
  onViewComments?: (recommendation: Recommendation) => void;
  onValidate: (recommendation: Recommendation) => void;
  hasActiveFilters?: boolean;
  onClearFilters?: () => void;
}

export function RecommendationsList({
  recommendations,
  onViewDetails,
  onViewComments,
  onValidate,
  hasActiveFilters = false,
  onClearFilters
}: RecommendationsListProps) {
  // Empty state
  if (recommendations.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="text-center py-16">
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-medium">No recommendations found</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                {hasActiveFilters 
                  ? "No recommendations match your current search criteria. Try adjusting your filters or search terms."
                  : "There are no recommendations available at this time. Check back later or refresh your data sources."
                }
              </p>
              {hasActiveFilters && onClearFilters && (
                <Button variant="outline" onClick={onClearFilters} className="mt-4">
                  Clear All Filters
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results summary with improved styling */}
      <div className="flex items-center justify-between py-6 border-b border-gray-100">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">
            Course Improvement Recommendations
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            AI-powered insights to enhance course quality and student experience
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 bg-blue-50 text-blue-700 text-sm font-medium rounded-full">
            {recommendations.length} recommendation{recommendations.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* 2-column grid layout with improved spacing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {recommendations.map((recommendation, index) => (
          <div
            key={recommendation.id}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <RecommendationCard
              recommendation={recommendation}
              onViewComments={onViewComments ? (rec) => onViewComments(rec) : undefined}
              onValidate={(rec) => onValidate(rec)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}