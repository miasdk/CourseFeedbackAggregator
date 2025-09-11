import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { ScoringWeights } from "../types";

interface ScoringControlsProps {
  weights: ScoringWeights;
  onWeightsChange: (weights: ScoringWeights) => void;
  onRecompute: () => void;
  onReset: () => void;
  isRecomputing: boolean;
}

export function ScoringControls({ 
  weights, 
  onWeightsChange, 
  onRecompute, 
  onReset, 
  isRecomputing 
}: ScoringControlsProps) {
  
  // Convert decimal weight (0-1) to 1-5 scale and vice versa
  const weightToScale = (weight: number): number => {
    return Math.round(weight * 4) + 1; // 0.0 -> 1, 0.25 -> 2, 0.5 -> 3, 0.75 -> 4, 1.0 -> 5
  };

  const scaleToWeight = (scale: number): number => {
    return (scale - 1) / 4; // 1 -> 0.0, 2 -> 0.25, 3 -> 0.5, 4 -> 0.75, 5 -> 1.0
  };

  const handleWeightChange = (factor: keyof ScoringWeights, value: number[]) => {
    const weightValue = scaleToWeight(value[0]);
    const newWeights = { ...weights, [factor]: weightValue };
    onWeightsChange(newWeights);
  };

  const factorConfig = {
    impact: {
      label: "Impact",
      description: "How many students are affected by this issue",
      color: "text-red-600"
    },
    urgency: {
      label: "Urgency", 
      description: "How time-critical is this issue",
      color: "text-orange-600"
    },
    effort: {
      label: "Effort",
      description: "Implementation complexity (lower effort = higher priority)", 
      color: "text-blue-600"
    },
    strategic: {
      label: "Strategic",
      description: "Alignment with course learning objectives",
      color: "text-green-600"
    },
    trend: {
      label: "Trend",
      description: "Is this issue getting worse over time",
      color: "text-purple-600"
    }
  };

  const getScaleLabel = (scale: number): string => {
    const labels = ['', 'Very Low', 'Low', 'Medium', 'High', 'Very High'];
    return labels[scale] || '';
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            Priority Scoring Weights
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onReset}>
            Reset
          </Button>
        </div>
        <p className="text-sm text-muted-foreground">
          Adjust the importance of each factor in priority calculation
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <TooltipProvider>
          {Object.entries(weights).map(([factor, weight]) => {
            const config = factorConfig[factor as keyof typeof factorConfig];
            const scaleValue = weightToScale(weight);
            return (
              <div key={factor} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Label className="text-sm font-medium">{config.label}</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs min-w-16 justify-center">
                      {scaleValue}/5
                    </Badge>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Slider
                    value={[scaleValue]}
                    onValueChange={(value: number[]) => handleWeightChange(factor as keyof ScoringWeights, value)}
                    max={5}
                    min={1}
                    step={1}
                    className="flex-1"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1 Low</span>
                    <span className="text-xs font-medium text-foreground">
                      {getScaleLabel(scaleValue)}
                    </span>
                    <span>5 High</span>
                  </div>
                </div>
              </div>
            );
          })}
        </TooltipProvider>

        <div className="pt-4 border-t">
          <Button 
            onClick={onRecompute} 
            disabled={isRecomputing}
            className="w-full"
            size="sm"
          >
            {isRecomputing ? (
              <>Recomputing Scores...</>
            ) : (
              <>Apply New Weights</>
            )}
          </Button>
          
          <p className="text-xs text-muted-foreground text-center mt-2">
            Changes are applied immediately. Click to recalculate all priority scores.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}