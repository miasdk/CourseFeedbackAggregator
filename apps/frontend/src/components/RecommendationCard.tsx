import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Eye, CheckCircle, AlertTriangle, Users, Clock } from "lucide-react";
import { Recommendation } from "../types";

interface RecommendationCardProps {
  recommendation: Recommendation;
  onViewDetails?: (recommendation: Recommendation) => void;
  onValidate?: (recommendation: Recommendation) => void;
}

export function RecommendationCard({ 
  recommendation, 
  onViewDetails,
  onValidate 
}: RecommendationCardProps) {
  
  const getPriorityColor = (score: number) => {
    if (score >= 5) return "bg-red-500 text-white";
    if (score >= 4) return "bg-orange-500 text-white";
    if (score >= 3) return "bg-yellow-500 text-black";
    return "bg-green-500 text-white";
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 5) return "CRITICAL";
    if (score >= 4) return "HIGH";
    if (score >= 3) return "MEDIUM";
    return "LOW";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-gray-100 text-gray-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge className={`${getPriorityColor(recommendation.priority_score)} text-xs font-bold`}>
                {getPriorityLabel(recommendation.priority_score)} {recommendation.priority_score}/5
              </Badge>
              {recommendation.is_show_stopper && (
                <Badge variant="destructive" className="text-xs">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  SHOW STOPPER
                </Badge>
              )}
              <Badge className={getStatusColor(recommendation.status)} variant="secondary">
                {recommendation.status.toUpperCase()}
              </Badge>
            </div>
            <h3 className="font-semibold text-sm leading-tight mb-1">
              {recommendation.title}
            </h3>
            <p className="text-xs text-muted-foreground mb-2">
              {recommendation.course_name} • {recommendation.category}
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-sm text-gray-700 mb-4 line-clamp-2">
          {recommendation.description}
        </p>
        
        <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
          <div className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {recommendation.affected_students} students
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {recommendation.feedback_count} reports
          </div>
        </div>

        {/* Score breakdown */}
        <div className="grid grid-cols-5 gap-2 mb-4 text-xs">
          <div className="text-center">
            <div className="font-medium text-red-600">{recommendation.impact_score}</div>
            <div className="text-muted-foreground">Impact</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-orange-600">{recommendation.urgency_score}</div>
            <div className="text-muted-foreground">Urgency</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-blue-600">{recommendation.effort_score}</div>
            <div className="text-muted-foreground">Effort</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-green-600">{recommendation.strategic_score}</div>
            <div className="text-muted-foreground">Strategic</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-purple-600">{recommendation.trend_score}</div>
            <div className="text-muted-foreground">Trend</div>
          </div>
        </div>
        
        <div className="flex gap-2">
          {onViewDetails && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onViewDetails(recommendation)}
              className="flex-1"
            >
              <Eye className="h-3 w-3 mr-1" />
              View Details
            </Button>
          )}
          {onValidate && recommendation.status === 'pending' && (
            <Button 
              variant="default" 
              size="sm" 
              onClick={() => onValidate(recommendation)}
              className="flex-1"
            >
              <CheckCircle className="h-3 w-3 mr-1" />
              Validate
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}