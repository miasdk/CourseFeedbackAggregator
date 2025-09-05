import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Zap, TrendingUp, CheckCircle, ArrowRight, Clock, Target } from 'lucide-react';

interface Course {
  id: string;
  title: string;
  category: string;
  rating: number;
  reviewCount: number;
  moduleCount: number;
  lastUpdated: string;
  lastUpdatedDate: Date; // Add actual date for sorting  
  criticalIssues: number;
  description?: string;
  instructor?: string;
  duration?: string;
}

interface ActionItem {
  type: 'critical' | 'quick-win' | 'improvement' | 'success';
  title: string;
  count: number;
  courses: Course[];
  description: string;
  priority: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
  impact: 'low' | 'medium' | 'high';
}

interface PriorityDashboardProps {
  courses: Course[];
  onActionClick?: (action: ActionItem) => void;
}

// Course Analysis Utilities
const analyzeCourses = (courses: Course[]): ActionItem[] => {
  // Critical Issues Analysis
  const criticalCourses = courses.filter(course => course.criticalIssues > 0);

  // Quick Wins Analysis (courses with good reviews but minor issues)
  const quickWinCourses = courses.filter(course => 
    course.rating >= 4.0 && course.criticalIssues <= 1 && course.reviewCount >= 2
  );

  // Improvement Opportunities (courses with potential)
  const improvementCourses = courses.filter(course => 
    course.rating >= 3.0 && course.rating < 4.0 && course.reviewCount >= 1
  );

  // High Performing Courses (success patterns)
  const successCourses = courses.filter(course => 
    course.rating >= 4.5 && course.criticalIssues === 0
  );

  return [
    {
      type: 'critical',
      title: 'Critical Issues',
      count: criticalCourses.length,
      courses: criticalCourses,
      description: `${criticalCourses.length} courses with critical issues`,
      priority: 'high',
      effort: 'medium',
      impact: 'high'
    },
    {
      type: 'quick-win',
      title: 'Quick Fixes',
      count: quickWinCourses.length,
      courses: quickWinCourses,
      description: `${quickWinCourses.length} courses with minor fixes`,
      priority: 'medium',
      effort: 'low',
      impact: 'medium'
    },
    {
      type: 'improvement',
      title: 'Improvements',
      count: improvementCourses.length,
      courses: improvementCourses,
      description: `${improvementCourses.length} courses to improve`,
      priority: 'medium',
      effort: 'medium',
      impact: 'high'
    },
    {
      type: 'success',
      title: 'Performing Well',
      count: successCourses.length,
      courses: successCourses,
      description: `${successCourses.length} high-performing courses`,
      priority: 'low',
      effort: 'low',
      impact: 'low'
    }
  ];
};

// Get visual styling for each action type
const getActionStyle = (type: ActionItem['type']) => {
  switch (type) {
    case 'critical':
      return {
        bgColor: 'bg-gray-50',
        iconBg: 'bg-gray-700',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200',
        icon: AlertTriangle,
        gradient: 'from-gray-600 to-gray-700'
      };
    case 'quick-win':
      return {
        bgColor: 'bg-gray-50',
        iconBg: 'bg-gray-600',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200',
        icon: Zap,
        gradient: 'from-gray-500 to-gray-600'
      };
    case 'improvement':
      return {
        bgColor: 'bg-gray-50',
        iconBg: 'bg-gray-600',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200',
        icon: TrendingUp,
        gradient: 'from-gray-500 to-gray-600'
      };
    case 'success':
      return {
        bgColor: 'bg-gray-50',
        iconBg: 'bg-gray-500',
        textColor: 'text-gray-700',
        borderColor: 'border-gray-200',
        icon: CheckCircle,
        gradient: 'from-gray-400 to-gray-500'
      };
    default:
      return {
        bgColor: 'bg-apple-50',
        iconBg: 'bg-apple-500',
        textColor: 'text-apple-700',
        borderColor: 'border-apple-200',
        icon: Target,
        gradient: 'from-apple-500 to-apple-600'
      };
  }
};

// Priority Badge Component
const PriorityBadge: React.FC<{ priority: ActionItem['priority'] }> = ({ priority }) => {
  const styles = {
    high: 'bg-gray-200 text-gray-800 border-gray-300',
    medium: 'bg-gray-100 text-gray-700 border-gray-200',
    low: 'bg-gray-50 text-gray-600 border-gray-200'
  };

  return (
    <span className={`text-xs px-2 py-1 rounded-full border ${styles[priority]} font-medium uppercase`}>
      {priority} Priority
    </span>
  );
};

// Effort/Impact Indicators
const EffortImpactIndicator: React.FC<{ effort: ActionItem['effort']; impact: ActionItem['impact'] }> = ({ effort, impact }) => {
  return (
    <div className="flex items-center space-x-3 text-xs text-apple-600">
      <div className="flex items-center space-x-1">
        <Clock className="w-3 h-3" />
        <span>Effort: {effort}</span>
      </div>
      <div className="flex items-center space-x-1">
        <Target className="w-3 h-3" />
        <span>Impact: {impact}</span>
      </div>
    </div>
  );
};

const PriorityDashboard: React.FC<PriorityDashboardProps> = ({ courses, onActionClick }) => {
  const actionItems = analyzeCourses(courses);

  const handleActionClick = (action: ActionItem) => {
    if (onActionClick) {
      onActionClick(action);
    } else {
      // Default behavior: log the action for now
      console.log(`Action clicked: ${action.type}`, action.courses);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {actionItems.map((action, index) => {
        const style = getActionStyle(action.type);
        const Icon = style.icon;

        return (
          <motion.div
            key={action.type}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className={`card-apple card-apple-hover cursor-pointer border ${style.borderColor} ${style.bgColor} hover:shadow-lg transition-all duration-200`}
            onClick={() => handleActionClick(action)}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 pb-4">
              <div className={`p-3 rounded-xl ${style.bgColor}`}>
                <div className={`${style.iconBg} p-2 rounded-lg text-white shadow-sm`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <PriorityBadge priority={action.priority} />
            </div>

            {/* Content */}
            <div className="px-6 pb-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className={`text-3xl font-bold ${style.textColor}`}>
                  {action.count}
                </h3>
                <ArrowRight className={`w-4 h-4 ${style.textColor} opacity-60`} />
              </div>
              
              <p className="text-sm font-semibold text-apple-900 mb-1">
                {action.title}
              </p>
              
              <p className="text-xs text-apple-600 mb-3">
                {action.description}
              </p>

              {/* Effort/Impact Indicators */}
              <EffortImpactIndicator effort={action.effort} impact={action.impact} />

              {/* Progress Bar */}
              <div className="mt-3 h-1.5 bg-apple-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: action.count > 0 ? `${Math.min((action.count / courses.length) * 100 * 4, 100)}%` : '0%' }}
                  transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
                  className={`h-full bg-gradient-to-r ${style.gradient} rounded-full`}
                />
              </div>

              {/* Course Examples */}
              {action.courses.length > 0 && (
                <div className="mt-3 text-xs text-apple-500">
                  Next: {action.courses[0].title.substring(0, 30)}
                  {action.courses[0].title.length > 30 ? '...' : ''}
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default PriorityDashboard; 