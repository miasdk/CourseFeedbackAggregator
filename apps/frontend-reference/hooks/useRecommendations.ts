import { useState, useMemo, useCallback } from "react";
import { Recommendation, ScoringWeights } from "../types";
import { mockRecommendations, defaultScoringWeights } from "../data/mockData";
import { toast } from "sonner@2.0.3";

export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>(mockRecommendations);
  const [scoringWeights, setScoringWeights] = useState<ScoringWeights>(defaultScoringWeights);
  const [isRecomputing, setIsRecomputing] = useState(false);

  const updateRecommendation = useCallback((recommendationId: string, updates: Partial<Recommendation>) => {
    setRecommendations(prev => 
      prev.map(rec => 
        rec.id === recommendationId 
          ? { ...rec, ...updates }
          : rec
      )
    );
  }, []);

  const validateRecommendation = useCallback((recommendation: Recommendation, notes: string, validator = 'Current User') => {
    updateRecommendation(recommendation.id, {
      status: 'validated' as const,
      validator,
      validation_notes: notes
    });
    toast.success(`Recommendation "${recommendation.title}" has been validated`);
  }, [updateRecommendation]);

  const recomputeScores = useCallback(async () => {
    if (isRecomputing) return;

    setIsRecomputing(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Calculate total weight for normalization (1-5 scale)
      const totalWeight = Object.values(scoringWeights).reduce((sum, weight) => sum + weight, 0);
      
      const updatedRecommendations = recommendations.map(rec => {
        // Normalize weights and calculate weighted score
        const normalizedScore = Math.round(
          (rec.impact_score * (scoringWeights.impact / totalWeight)) +
          (rec.urgency_score * (scoringWeights.urgency / totalWeight)) +
          ((100 - rec.effort_score) * (scoringWeights.effort / totalWeight)) +
          (rec.strategic_score * (scoringWeights.strategic / totalWeight)) +
          (rec.trend_score * (scoringWeights.trend / totalWeight))
        );
        
        return { ...rec, priority_score: Math.min(100, Math.max(0, normalizedScore)) };
      });
      
      setRecommendations(updatedRecommendations);
      toast.success("Scores have been recomputed with new weights");
    } catch (error) {
      toast.error("Failed to recompute scores. Please try again.");
    } finally {
      setIsRecomputing(false);
    }
  }, [recommendations, scoringWeights, isRecomputing]);

  const resetWeights = useCallback(() => {
    setScoringWeights(defaultScoringWeights);
    toast.info("Scoring weights reset to defaults");
  }, []);

  const stats = useMemo(() => ({
    showStoppers: recommendations.filter(r => r.is_show_stopper).length,
    pending: recommendations.filter(r => r.status === 'pending').length,
    validated: recommendations.filter(r => r.status === 'validated').length,
    inProgress: recommendations.filter(r => r.status === 'in_progress').length,
    averageScore: recommendations.length > 0 
      ? Math.round(recommendations.reduce((sum, r) => sum + r.priority_score, 0) / recommendations.length)
      : 0
  }), [recommendations]);

  return {
    recommendations,
    scoringWeights,
    setScoringWeights,
    isRecomputing,
    updateRecommendation,
    validateRecommendation,
    recomputeScores,
    resetWeights,
    stats
  };
}