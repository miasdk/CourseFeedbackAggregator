import { useState, useMemo, useCallback } from "react";
import { Recommendation } from "../types";

export function useFilters(recommendations: Recommendation[]) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const filteredRecommendations = useMemo(() => {
    return recommendations
      .filter(rec => {
        const matchesSearch = searchQuery === "" || [
          rec.title,
          rec.description,
          rec.course_name
        ].some(field => field.toLowerCase().includes(searchQuery.toLowerCase()));
        
        const matchesStatus = statusFilter === "all" || rec.status === statusFilter;
        const matchesCategory = categoryFilter === "all" || rec.category === categoryFilter;
        
        return matchesSearch && matchesStatus && matchesCategory;
      })
      .sort((a, b) => {
        // Prioritize show stoppers, then by priority score
        if (a.is_show_stopper && !b.is_show_stopper) return -1;
        if (!a.is_show_stopper && b.is_show_stopper) return 1;
        return b.priority_score - a.priority_score;
      });
  }, [recommendations, searchQuery, statusFilter, categoryFilter]);

  const clearFilters = useCallback(() => {
    setSearchQuery("");
    setStatusFilter("all");
    setCategoryFilter("all");
  }, []);

  const hasActiveFilters = useMemo(() => {
    return searchQuery !== "" || statusFilter !== "all" || categoryFilter !== "all";
  }, [searchQuery, statusFilter, categoryFilter]);

  return {
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    categoryFilter,
    setCategoryFilter,
    filteredRecommendations,
    clearFilters,
    hasActiveFilters
  };
}