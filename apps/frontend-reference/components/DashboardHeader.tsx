/**
 * Simplified Dashboard Header Component
 * 
 * Clean, minimal header for the dashboard with essential controls
 */

import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { Search, RefreshCw, Download, Filter } from "lucide-react";

interface DashboardHeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  categoryFilter: string;
  onCategoryFilterChange: (category: string) => void;
  totalRecommendations: number;
  filteredCount: number;
  onRefresh: () => void;
  isRefreshing: boolean;
}

/**
 * Simplified dashboard header with reduced visual clutter
 * Focuses on essential filtering and search functionality
 */
export function DashboardHeader({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
  categoryFilter,
  onCategoryFilterChange,
  totalRecommendations,
  filteredCount,
  onRefresh,
  isRefreshing
}: DashboardHeaderProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      {/* Left side - Search and filters */}
      <div className="flex items-center gap-3 flex-1">
        <div className="relative w-80">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search recommendations..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select value={statusFilter} onValueChange={onStatusFilterChange}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="validated">Validated</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>

        <Select value={categoryFilter} onValueChange={onCategoryFilterChange}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="technical">Technical</SelectItem>
            <SelectItem value="content">Content</SelectItem>
            <SelectItem value="assessment">Assessment</SelectItem>
            <SelectItem value="navigation">Navigation</SelectItem>
            <SelectItem value="other">Other</SelectItem>
          </SelectContent>
        </Select>

        {/* Results count */}
        <Badge variant="secondary" className="text-xs">
          {filteredCount} of {totalRecommendations}
        </Badge>
      </div>

      {/* Right side - Actions */}
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={onRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </Button>
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}