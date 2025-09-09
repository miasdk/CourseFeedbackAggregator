import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "./ui/sheet";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Separator } from "./ui/separator";
import { Progress } from "./ui/progress";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { AlertTriangle, Users, MessageSquare, ExternalLink, TrendingUp, Target, Zap, Clock, Star } from "lucide-react";
import { useState } from "react";
import { Recommendation, ScoringWeights } from "../types";

interface RecommendationDetailsProps {
  recommendation: Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
  onValidate: (recommendation: Recommendation, notes: string) => void;
  scoringWeights: ScoringWeights;
}

export function RecommendationDetails({ 
  recommendation, 
  isOpen, 
  onClose, 
  onValidate, 
  scoringWeights 
}: RecommendationDetailsProps) {
  const [validationNotes, setValidationNotes] = useState("");
  const [isValidating, setIsValidating] = useState(false);

  if (!recommendation) return null;

  const handleValidate = async () => {
    if (!validationNotes.trim()) return;
    
    setIsValidating(true);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
    onValidate(recommendation, validationNotes);
    setValidationNotes("");
    setIsValidating(false);
    onClose();
  };

  const convertToFivePointScale = (score: number): number => {
    // Convert 0-100 score to 1-5 scale
    return Math.max(1, Math.min(5, Math.round((score / 100) * 4) + 1));
  };

  const ScoreBreakdown = () => {
    const factors = [
      { name: 'Impact', score: recommendation.impact_score, weight: scoringWeights.impact, icon: Users },
      { name: 'Urgency', score: recommendation.urgency_score, weight: scoringWeights.urgency, icon: AlertTriangle },
      { name: 'Effort', score: 100 - recommendation.effort_score, weight: scoringWeights.effort, icon: Zap }, // Inverted for display
      { name: 'Strategic', score: recommendation.strategic_score, weight: scoringWeights.strategic, icon: Target },
      { name: 'Trend', score: recommendation.trend_score, weight: scoringWeights.trend, icon: TrendingUp }
    ];

    // Calculate total weight for normalization
    const totalWeight = Object.values(scoringWeights).reduce((sum, weight) => sum + weight, 0);

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Star className="h-5 w-5" />
            Score Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <div className="text-3xl font-bold mb-1">{convertToFivePointScale(recommendation.priority_score)}/5</div>
            <div className="text-sm text-muted-foreground">Priority Score</div>
          </div>
          
          <Separator />
          
          {factors.map((factor) => {
            const Icon = factor.icon;
            const normalizedWeight = (factor.weight / totalWeight) * 100;
            const weightedScore = (factor.score * normalizedWeight) / 100;
            
            return (
              <div key={factor.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    <span className="text-sm font-medium">{factor.name}</span>
                    <Badge variant="outline" className="text-xs">Weight: {factor.weight}/5</Badge>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{factor.score}/100</div>
                    <div className="text-xs text-muted-foreground">+{weightedScore.toFixed(1)} points</div>
                  </div>
                </div>
                <Progress value={factor.score} className="h-2" />
              </div>
            );
          })}
        </CardContent>
      </Card>
    );
  };

  const FeedbackQuotes = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Student Feedback ({recommendation.related_feedback.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recommendation.related_feedback.slice(0, 3).map((feedback) => (
          <div key={feedback.id} className="border-l-4 border-muted pl-4 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">{feedback.source}</Badge>
                {feedback.is_show_stopper && (
                  <Badge variant="outline" className="text-xs gap-1">
                    <AlertTriangle className="h-3 w-3" />
                    Blocker
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-1">
                <span className="text-xs text-muted-foreground">Rating:</span>
                <span className="text-sm font-medium">{feedback.rating}/5</span>
              </div>
            </div>
            <p className="text-sm leading-relaxed">{feedback.comment}</p>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{feedback.module_name}</span>
              <Button variant="ghost" size="sm" className="h-auto p-0 text-xs">
                <ExternalLink className="h-3 w-3 mr-1" />
                View in {feedback.source}
              </Button>
            </div>
          </div>
        ))}
        
        {recommendation.related_feedback.length > 3 && (
          <Button variant="outline" size="sm" className="w-full">
            View {recommendation.related_feedback.length - 3} more feedback items
          </Button>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-2xl overflow-y-auto">
        <SheetHeader className="space-y-3">
          <div className="flex items-start justify-between">
            <SheetTitle className="text-left pr-4">{recommendation.title}</SheetTitle>
            {recommendation.is_show_stopper && (
              <Badge variant="outline" className="gap-1 shrink-0">
                <AlertTriangle className="h-3 w-3" />
                Show Stopper
              </Badge>
            )}
          </div>
          <SheetDescription className="text-left">
            {recommendation.course_name} • {recommendation.category}
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          <div>
            <h4 className="font-medium mb-2">Description</h4>
            <p className="text-sm leading-relaxed">{recommendation.description}</p>
          </div>

          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="space-y-1">
              <div className="text-2xl font-bold">{recommendation.affected_students}</div>
              <div className="text-xs text-muted-foreground">Students Affected</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold">{recommendation.feedback_count}</div>
              <div className="text-xs text-muted-foreground">Feedback Items</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold">
                {recommendation.effort_score <= 30 ? 'Low' : recommendation.effort_score <= 70 ? 'Med' : 'High'}
              </div>
              <div className="text-xs text-muted-foreground">Effort Required</div>
            </div>
          </div>

          <ScoreBreakdown />
          
          <FeedbackQuotes />

          {recommendation.status === 'pending' && (
            <Card>
              <CardHeader>
                <CardTitle>Validate Recommendation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="validation-notes">Validation Notes</Label>
                  <Textarea
                    id="validation-notes"
                    placeholder="Add your validation notes, implementation plan, or concerns..."
                    value={validationNotes}
                    onChange={(e) => setValidationNotes(e.target.value)}
                    rows={3}
                  />
                </div>
                <Button 
                  onClick={handleValidate} 
                  disabled={!validationNotes.trim() || isValidating}
                  className="w-full"
                >
                  {isValidating ? "Validating..." : "Validate Recommendation"}
                </Button>
              </CardContent>
            </Card>
          )}

          {recommendation.status === 'validated' && recommendation.validation_notes && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Validation Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm"><strong>Validated by:</strong> {recommendation.validator}</p>
                  <p className="text-sm leading-relaxed">{recommendation.validation_notes}</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}