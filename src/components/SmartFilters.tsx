import React from 'react';
import { motion } from 'framer-motion';
import { Filter, X, AlertTriangle, Clock, Zap, CheckCircle } from 'lucide-react';
import { ISSUE_CATEGORIES } from '../services/issueAnalysis';

export interface SmartFiltersProps {
  // Filter states
  selectedIssueCategories: string[];
  selectedPriorityLevels: string[];
  selectedActionStatus: string[];
  showOnlyWithActions: boolean;
  
  // Filter actions
  onIssueCategoryToggle: (category: string) => void;
  onPriorityLevelToggle: (priority: string) => void;
  onActionStatusToggle: (status: string) => void;
  onToggleShowOnlyWithActions: () => void;
  onClearFilters: () => void;
  
  // Counts for display
  filteredCount: number;
  totalCount: number;
}

const PRIORITY_LEVELS = [
  { id: 'urgent', name: 'Urgent', icon: '🔴', color: 'red' },
  { id: 'high', name: 'High', icon: '🟡', color: 'orange' },
  { id: 'medium', name: 'Medium', icon: '⚡', color: 'yellow' },
  { id: 'low', name: 'Low', icon: '✅', color: 'green' }
];

const ACTION_STATUS = [
  { id: 'pending', name: 'Needs Action', icon: <Clock className="w-4 h-4" />, color: 'orange' },
  { id: 'in-progress', name: 'In Progress', icon: <Zap className="w-4 h-4" />, color: 'blue' },
  { id: 'completed', name: 'Resolved', icon: <CheckCircle className="w-4 h-4" />, color: 'green' }
];

const SmartFilters: React.FC<SmartFiltersProps> = ({
  selectedIssueCategories,
  selectedPriorityLevels,
  selectedActionStatus,
  showOnlyWithActions,
  onIssueCategoryToggle,
  onPriorityLevelToggle,
  onActionStatusToggle,
  onToggleShowOnlyWithActions,
  onClearFilters,
  filteredCount,
  totalCount
}) => {
  const hasActiveFilters = 
    selectedIssueCategories.length > 0 || 
    selectedPriorityLevels.length > 0 || 
    selectedActionStatus.length > 0 || 
    showOnlyWithActions;

  const activeFilterCount = selectedIssueCategories.length + selectedPriorityLevels.length + selectedActionStatus.length + (showOnlyWithActions ? 1 : 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-sm border border-apple-200 p-6 mb-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Filter className="w-5 h-5 text-apple-600" />
          <h3 className="text-lg font-semibold text-apple-900">Smart Filters</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-apple-500">
              Showing {filteredCount} of {totalCount} courses
            </span>
            {hasActiveFilters && (
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
                {activeFilterCount} active
              </span>
            )}
          </div>
        </div>
        
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="flex items-center space-x-2 text-sm text-apple-500 hover:text-red-600 transition-colors"
          >
            <X className="w-4 h-4" />
            <span>Clear All</span>
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Issue Categories */}
        <div>
          <h4 className="text-sm font-semibold text-apple-700 mb-4 flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Issue Categories
            {selectedIssueCategories.length > 0 && (
              <span className="ml-2 bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs">
                {selectedIssueCategories.length}
              </span>
            )}
          </h4>
          <div className="space-y-2">
            {Object.values(ISSUE_CATEGORIES).map((category) => (
              <motion.button
                key={category.id}
                onClick={() => onIssueCategoryToggle(category.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                  selectedIssueCategories.includes(category.id)
                    ? 'border-blue-200 bg-blue-50 shadow-sm'
                    : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-lg">{category.icon}</span>
                <div className="flex-1 text-left">
                  <div className={`text-sm font-medium ${
                    selectedIssueCategories.includes(category.id) ? 'text-blue-900' : 'text-gray-900'
                  }`}>
                    {category.name}
                  </div>
                  <div className={`text-xs truncate ${
                    selectedIssueCategories.includes(category.id) ? 'text-blue-600' : 'text-gray-500'
                  }`}>
                    {category.description}
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Priority Levels */}
        <div>
          <h4 className="text-sm font-semibold text-apple-700 mb-4 flex items-center">
            <span className="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
            Priority Levels
            {selectedPriorityLevels.length > 0 && (
              <span className="ml-2 bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full text-xs">
                {selectedPriorityLevels.length}
              </span>
            )}
          </h4>
          <div className="space-y-2">
            {PRIORITY_LEVELS.map((priority) => (
              <motion.button
                key={priority.id}
                onClick={() => onPriorityLevelToggle(priority.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                  selectedPriorityLevels.includes(priority.id)
                    ? 'border-orange-200 bg-orange-50 shadow-sm'
                    : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-lg">{priority.icon}</span>
                <div className={`text-sm font-medium ${
                  selectedPriorityLevels.includes(priority.id) ? 'text-orange-900' : 'text-gray-900'
                }`}>
                  {priority.name}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Action Status & Quick Actions */}
        <div>
          <h4 className="text-sm font-semibold text-apple-700 mb-4 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Action Status
            {selectedActionStatus.length > 0 && (
              <span className="ml-2 bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs">
                {selectedActionStatus.length}
              </span>
            )}
          </h4>
          <div className="space-y-2 mb-4">
            {ACTION_STATUS.map((status) => (
              <motion.button
                key={status.id}
                onClick={() => onActionStatusToggle(status.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                  selectedActionStatus.includes(status.id)
                    ? 'border-green-200 bg-green-50 shadow-sm'
                    : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {status.icon}
                <div className={`text-sm font-medium ${
                  selectedActionStatus.includes(status.id) ? 'text-green-900' : 'text-gray-900'
                }`}>
                  {status.name}
                </div>
              </motion.button>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="border-t border-gray-200 pt-4">
            <h5 className="text-xs font-semibold text-gray-600 mb-3 uppercase tracking-wide">Quick Actions</h5>
            <motion.button
              onClick={onToggleShowOnlyWithActions}
              className={`w-full flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                showOnlyWithActions
                  ? 'border-blue-200 bg-blue-50 shadow-sm'
                  : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <AlertTriangle className={`w-4 h-4 ${showOnlyWithActions ? 'text-blue-600' : 'text-gray-600'}`} />
              <div className={`text-sm font-medium ${
                showOnlyWithActions ? 'text-blue-900' : 'text-gray-900'
              }`}>
                Only Action Items
              </div>
            </motion.button>
          </div>
        </div>
      </div>

      {/* Results Summary - Only show when filters are active */}
      {hasActiveFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 pt-4 border-t border-gray-200"
        >
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                <span className="font-medium text-gray-900">{filteredCount}</span> of <span className="font-medium text-gray-900">{totalCount}</span> courses match your filters
              </div>
              <div className="text-xs text-gray-500">
                {Math.round((filteredCount / totalCount) * 100)}% of total courses
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default SmartFilters; 