/**
 * Scoring Controls Component
 * 
 * Professional scoring weight controls using 1-5 scale
 * for course improvement recommendation prioritization
 */

import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Label } from "./ui/label";
import { Slider } from "./ui/slider";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Info, RotateCcw, Calculator } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import { ScoringWeights } from "../types";

interface ScoringControlsProps {
  weights: ScoringWeights;
  onWeightsChange: (weights: ScoringWeights) => void;
  onRecompute: () => void;
  onReset: () => void;
  isRecomputing: boolean;
}

/**
 * Professional scoring controls with 1-5 scale instead of percentages
 * Provides intuitive weight adjustment for recommendation scoring
 */
export function ScoringControls({ 
  weights, 
  onWeightsChange, 
  onRecompute, 
  onReset, 
  isRecomputing 
}: ScoringControlsProps) {
  
  const handleWeightChange = (factor: keyof ScoringWeights, value: number[]) => {
    const newWeights = { ...weights, [factor]: value[0] };
    onWeightsChange(newWeights);
  };

  const factorConfig = {
    impact: {
      label: "Impact",
      description: "Number of students affected by this issue",
      color: "text-red-600"
    },
    urgency: {
      label: "Urgency", 
      description: "How critical is this issue? Show-stoppers score higher",
      color: "text-orange-600"
    },
    effort: {
      label: "Effort",
      description: "Implementation complexity - lower effort scores higher", 
      color: "text-blue-600"
    },
    strategic: {
      label: "Strategic",
      description: "Alignment with course learning objectives",
      color: "text-green-600"
    },
    trend: {
      label: "Trend",
      description: "Is this issue getting worse over time?",
      color: "text-purple-600"
    }
  };

  const getScaleLabel = (value: number): string => {
    const labels = ['', 'Low', 'Below Avg', 'Average', 'Above Avg', 'High'];
    return labels[value] || '';
  };

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">
            Scoring Weights
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onReset} className="h-8 w-8 p-0">
            <RotateCcw className="h-3 w-3" />
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-5">
        <TooltipProvider>
          {Object.entries(weights).map(([factor, weight]) => {
            const config = factorConfig[factor as keyof typeof factorConfig];
            return (
              <div key={factor} className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Label className="text-sm font-medium">{config.label}</Label>
                    <Tooltip>
                      <TooltipTrigger>
                        <Info className="h-3 w-3 text-muted-foreground hover:text-foreground transition-colors" />
                      </TooltipTrigger>
                      <TooltipContent side="right" className="max-w-64">
                        <p className="text-xs">{config.description}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs min-w-16 justify-center">
                      {weight}/5
                    </Badge>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Slider
                    value={[weight]}
                    onValueChange={(value) => handleWeightChange(factor as keyof ScoringWeights, value)}
                    max={5}
                    min={1}
                    step={1}
                    className="flex-1"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Low</span>
                    <span className="text-xs font-medium text-foreground">
                      {getScaleLabel(weight)}
                    </span>
                    <span>High</span>
                  </div>
                </div>
              </div>
            );
          })}
        </TooltipProvider>

        <div className="pt-2 border-t">
          <Button 
            onClick={onRecompute} 
            disabled={isRecomputing}
            className="w-full"
            size="sm"
          >
            {isRecomputing ? (
              <>
                <Calculator className="h-4 w-4 mr-2 animate-pulse" />
                Recomputing...
              </>
            ) : (
              <>
                <Calculator className="h-4 w-4 mr-2" />
                Recompute Scores
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}