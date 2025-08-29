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
      title: 'URGENT ACTIONS',
      count: criticalCourses.length,
      courses: criticalCourses,
      description: `${criticalCourses.length} courses need immediate attention`,
      priority: 'high',
      effort: 'medium',
      impact: 'high'
    },
    {
      type: 'quick-win',
      title: 'QUICK WINS',
      count: quickWinCourses.length,
      courses: quickWinCourses,
      description: `${quickWinCourses.length} easy improvements available`,
      priority: 'medium',
      effort: 'low',
      impact: 'medium'
    },
    {
      type: 'improvement',
      title: 'IMPROVEMENT OPPORTUNITIES',
      count: improvementCourses.length,
      courses: improvementCourses,
      description: `${improvementCourses.length} courses with potential`,
      priority: 'medium',
      effort: 'medium',
      impact: 'high'
    },
    {
      type: 'success',
      title: 'PERFORMING WELL',
      count: successCourses.length,
      courses: successCourses,
      description: `${successCourses.length} courses exceeding expectations`,
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
        bgColor: 'bg-red-50',
        iconBg: 'bg-red-500',
        textColor: 'text-red-700',
        borderColor: 'border-red-200',
        icon: AlertTriangle,
        gradient: 'from-red-500 to-red-600'
      };
    case 'quick-win':
      return {
        bgColor: 'bg-yellow-50',
        iconBg: 'bg-yellow-500',
        textColor: 'text-yellow-700',
        borderColor: 'border-yellow-200',
        icon: Zap,
        gradient: 'from-yellow-500 to-yellow-600'
      };
    case 'improvement':
      return {
        bgColor: 'bg-blue-50',
        iconBg: 'bg-blue-500',
        textColor: 'text-blue-700',
        borderColor: 'border-blue-200',
        icon: TrendingUp,
        gradient: 'from-blue-500 to-blue-600'
      };
    case 'success':
      return {
        bgColor: 'bg-green-50',
        iconBg: 'bg-green-500',
        textColor: 'text-green-700',
        borderColor: 'border-green-200',
        icon: CheckCircle,
        gradient: 'from-green-500 to-green-600'
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
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200'
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