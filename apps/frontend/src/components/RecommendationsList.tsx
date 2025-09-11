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
      {/* Results summary */}
      <div className="flex items-center justify-between pt-4">
        <h2 className="text-lg font-medium">
          Course Improvement Recommendations
        </h2>
        <span className="text-sm text-muted-foreground">
          {recommendations.length} recommendation{recommendations.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* 2-column grid layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {recommendations.map((recommendation) => (
          <RecommendationCard
            key={recommendation.id}
            recommendation={recommendation}
            onViewComments={onViewComments ? (rec) => onViewComments(rec) : undefined}
            onValidate={(rec) => onValidate(rec)}
          />
        ))}
      </div>
    </div>
  );
}