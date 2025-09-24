import { useState, useEffect, useCallback } from 'react';
import { Recommendation, ScoringWeights } from '../types';
import { apiClient } from '../services/api';
import { toast } from 'sonner';

const defaultWeights: ScoringWeights = {
  impact: 4,
  urgency: 4,
  effort: 3,
  strategic: 2,
  trend: 2
};

export function useRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [scoringWeights, setScoringWeights] = useState<ScoringWeights>(defaultWeights);
  const [isLoading, setIsLoading] = useState(true);
  const [isRecomputing, setIsRecomputing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [recommendationsData, weightsData] = await Promise.all([
        apiClient.getPriorities(),
        apiClient.getWeights().catch(() => defaultWeights) // Fallback to defaults if weights endpoint fails
      ]);
      
      setRecommendations(recommendationsData);
      setScoringWeights(weightsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      toast.error('Failed to load recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateWeights = useCallback(async (newWeights: ScoringWeights) => {
    setScoringWeights(newWeights);
    
    try {
      await apiClient.updateWeights(newWeights);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update weights');
      toast.error('Failed to update scoring weights');
      // Revert weights on failure
      setScoringWeights(scoringWeights);
    }
  }, [scoringWeights]);

  const recomputeScores = useCallback(async () => {
    if (isRecomputing) return;
    
    setIsRecomputing(true);
    
    try {
      await apiClient.recomputePriorities();
      const updatedRecommendations = await apiClient.getPriorities();
      setRecommendations(updatedRecommendations);
      toast.success('Priority scores have been recomputed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to recompute scores');
      toast.error('Failed to recompute priority scores. Please try again.');
    } finally {
      setIsRecomputing(false);
    }
  }, [isRecomputing]);

  const resetWeights = useCallback(async () => {
    try {
      const resetWeightsData = await apiClient.resetWeights();
      setScoringWeights(resetWeightsData);
      toast.info('Scoring weights reset to defaults');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset weights');
      toast.error('Failed to reset weights');
    }
  }, []);

  const validateRecommendation = useCallback(async (
    recommendation: Recommendation, 
    notes: string, 
    validator = 'Current User'
  ) => {
    try {
      await apiClient.validateRecommendation(recommendation.id, notes, validator);
      
      // Update local state
      setRecommendations(prev => prev.map(rec => 
        rec.id === recommendation.id 
          ? { ...rec, status: 'validated' as const, validator, validation_notes: notes }
          : rec
      ));
      
      toast.success(`Recommendation "${recommendation.title}" has been validated`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate recommendation');
      toast.error('Failed to validate recommendation');
    }
  }, []);

  // Computed stats
  const stats = {
    total: recommendations.length,
    showStoppers: recommendations.filter(r => r.is_show_stopper).length,
    pending: recommendations.filter(r => r.status === 'pending').length,
    validated: recommendations.filter(r => r.status === 'validated').length,
    averageScore: recommendations.length > 0 
      ? Math.round(recommendations.reduce((sum, r) => sum + r.priority_score, 0) / recommendations.length)
      : 0
  };

  return {
    recommendations,
    scoringWeights,
    isLoading,
    isRecomputing,
    error,
    stats,
    updateWeights,
    recomputeScores,
    resetWeights,
    validateRecommendation,
    refresh: loadData
  };
}