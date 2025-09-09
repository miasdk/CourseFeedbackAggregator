/**
 * Recommendation Card Component
 * 
 * Professional card design for displaying course improvement recommendations
 * Optimized for 2-column grid layout with enhanced visual hierarchy
 */

import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Progress } from "./ui/progress";
import { AlertTriangle, Users, MessageSquare, Eye, CheckCircle, Clock, ArrowRight, Zap } from "lucide-react";
import { Recommendation } from "../types";

interface RecommendationCardProps {
  recommendation: Recommendation;
  onViewDetails: (recommendation: Recommendation) => void;
  onValidate: (recommendation: Recommendation) => void;
}

/**
 * Enhanced recommendation card with professional styling
 * Designed for optimal readability in 2-column grid layout
 */
export function RecommendationCard({ recommendation, onViewDetails, onValidate }: RecommendationCardProps) {
  const getPriorityColor = (score: number) => {
    if (score >= 85) return "bg-red-500";
    if (score >= 70) return "bg-orange-500";
    if (score >= 50) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 85) return "Critical";
    if (score >= 70) return "High";
    if (score >= 50) return "Medium";
    return "Low";
  };

  const convertToFivePointScale = (score: number): number => {
    // Convert 0-100 score to 1-5 scale
    return Math.max(1, Math.min(5, Math.round((score / 100) * 4) + 1));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'validated':
        return <CheckCircle className="h-4 w-4" />;
      case 'in_progress':
        return <Clock className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getEffortLabel = (score: number) => {
    if (score <= 30) return "Low";
    if (score <= 70) return "Medium";
    return "High";
  };

  return (
    <Card className="relative hover:shadow-md transition-shadow duration-200">
      
      {/* Priority Indicator */}
      <div className="absolute top-0 left-0 w-1 h-full rounded-l-lg" 
           style={{ backgroundColor: getPriorityColor(recommendation.priority_score).replace('bg-', '#') }}>
      </div>

      {/* Show Stopper Badge */}
      {recommendation.is_show_stopper && (
        <div className="absolute top-3 right-3 space-y-1">
          <Badge variant="outline" className="gap-1 text-xs">
            <AlertTriangle className="h-3 w-3" />
            Critical
          </Badge>
          {recommendation.status === 'validated' && (
            <div>
              <Badge variant="outline" className="gap-1 text-xs bg-green-50 text-green-700 border-green-200">
                <CheckCircle className="h-3 w-3" />
                Validated
              </Badge>
            </div>
          )}
        </div>
      )}

      {/* Validated Badge for non-critical tasks */}
      {!recommendation.is_show_stopper && recommendation.status === 'validated' && (
        <div className="absolute top-3 right-3">
          <Badge variant="outline" className="gap-1 text-xs bg-green-50 text-green-700 border-green-200">
            <CheckCircle className="h-3 w-3" />
            Validated
          </Badge>
        </div>
      )}
      
      <CardHeader className="pb-3 pl-5">
        <div className="flex items-start justify-between">
          <div className="space-y-1 flex-1 pr-4">
            <CardTitle className="text-base leading-tight">{recommendation.title}</CardTitle>
            <p className="text-sm text-muted-foreground">{recommendation.course_name}</p>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(recommendation.status)}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pl-5">
        <p className="text-sm leading-relaxed text-muted-foreground line-clamp-2">
          {recommendation.description}
        </p>
        
        {/* Priority Score Section */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-medium">Priority Score</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {getPriorityLabel(recommendation.priority_score)}
              </Badge>
              <span className="text-sm font-medium">{convertToFivePointScale(recommendation.priority_score)}/5</span>
            </div>
          </div>
          <Progress value={recommendation.priority_score} className="h-2" />
        </div>

        {/* Metrics */}
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>{recommendation.affected_students}</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare className="h-4 w-4" />
            <span>{recommendation.feedback_count}</span>
          </div>
          <Badge variant="secondary" className="text-xs capitalize">
            {recommendation.category}
          </Badge>
        </div>

        {/* Validation Notes */}
        {recommendation.status === 'validated' && recommendation.validation_notes && (
          <div className="p-3 bg-muted/50 border rounded-md">
            <p className="text-sm">
              <span className="font-medium">Validated:</span> {recommendation.validation_notes}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => onViewDetails(recommendation)}
            className="flex-1"
          >
            <Eye className="h-4 w-4 mr-2" />
            Details
          </Button>
          
          {recommendation.status === 'pending' && (
            <Button 
              size="sm" 
              onClick={() => onValidate(recommendation)}
              className="flex-1"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Validate
            </Button>
          )}
          
          {recommendation.status === 'validated' && (
            <Button size="sm" className="flex-1" variant="default">
              <ArrowRight className="h-4 w-4 mr-2" />
              Implement
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}