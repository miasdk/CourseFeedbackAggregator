import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Eye, CheckCircle, AlertTriangle, Users, Clock, MessageSquare } from "lucide-react";
import { Recommendation } from "../types";

interface RecommendationCardProps {
  recommendation: Recommendation;
  onViewDetails?: (recommendation: Recommendation) => void;
  onViewComments?: (recommendation: Recommendation) => void;
  onValidate?: (recommendation: Recommendation) => void;
}

export function RecommendationCard({ 
  recommendation, 
  onViewDetails,
  onViewComments,
  onValidate 
}: RecommendationCardProps) {
  
  const getPriorityColor = (score: number) => {
    return "bg-slate-100 text-slate-700 border border-slate-200";
  };

  const getPriorityLabel = (score: number) => {
    if (score >= 5) return "Critical";
    if (score >= 4) return "High";
    if (score >= 3) return "Medium";
    return "Low";
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
                {getPriorityLabel(recommendation.priority_score)} {recommendation.priority_score}
              </Badge>
              {recommendation.is_show_stopper && (
                <Badge variant="destructive" className="text-xs">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  SHOW STOPPER
                </Badge>
              )}
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

        
        <div className="flex gap-2">
          {onViewComments && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onViewComments(recommendation)}
              className="flex-1"
            >
              <MessageSquare className="h-3 w-3 mr-1" />
              Comments
            </Button>
          )}
          {onValidate && (
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