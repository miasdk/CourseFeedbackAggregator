import React from 'react';
import { AlertTriangle, Users, MessageSquare, ExternalLink } from 'lucide-react';
import { Course } from '../types';

interface CourseCardProps {
  course: Course;
  onViewDetails?: () => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onViewDetails }) => {
  // Calculate priority score (simplified)
  const priorityScore = course.analyticsData?.priorityScore || Math.random() * 10;
  
  // Get priority styling
  const getPriorityStyle = (score: number) => {
    if (score >= 8) return { 
      color: 'text-red-700', 
      bg: 'bg-red-50', 
      border: 'border-red-200',
      label: 'Critical'
    };
    if (score >= 6) return { 
      color: 'text-orange-700', 
      bg: 'bg-orange-50', 
      border: 'border-orange-200',
      label: 'High'
    };
    if (score >= 4) return { 
      color: 'text-yellow-700', 
      bg: 'bg-yellow-50', 
      border: 'border-yellow-200',
      label: 'Medium'
    };
    return { 
      color: 'text-gray-600', 
      bg: 'bg-gray-50', 
      border: 'border-gray-200',
      label: 'Low'
    };
  };

  const priorityStyle = getPriorityStyle(priorityScore);

  // Get feedback summary
  const totalIssues = course.issues?.length || 0;
  const studentsAffected = course.reviewCount || 0;

  return (
    <div className="bg-white border border-gray-200 hover:border-gray-300 transition-colors">
      {/* Priority Header */}
      <div className={`px-4 py-2 ${priorityStyle.bg} ${priorityStyle.border} border-b`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`text-xs font-medium ${priorityStyle.color}`}>
              {priorityStyle.label} Priority
            </div>
            <div className="text-sm font-bold text-gray-900">
              {priorityScore.toFixed(1)}
            </div>
          </div>
          {course.criticalIssues > 0 && (
            <div className="flex items-center gap-1">
              <AlertTriangle className="w-3 h-3 text-red-500" />
              <span className="text-xs text-red-700 font-medium">
                {course.criticalIssues} Critical
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Course Content */}
      <div className="p-4">
        {/* Course Title */}
        <h3 className="font-semibold text-gray-900 text-sm mb-2 leading-tight">
          {course.title}
        </h3>

        {/* Category */}
        <div className="mb-3">
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1">
            {course.category}
          </span>
        </div>

        {/* Feedback Summary */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-1">
              <MessageSquare className="w-3 h-3" />
              <span>{totalIssues} issues reported</span>
            </div>
            <div className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              <span>{studentsAffected} students</span>
            </div>
          </div>
          
          <div className="text-xs text-gray-600">
            Rating: {course.rating.toFixed(1)}/5.0
          </div>
        </div>

        {/* Top Issues Preview */}
        {course.issues && course.issues.length > 0 && (
          <div className="mb-4">
            <div className="text-xs text-gray-500 mb-1">Recent Issues:</div>
            <div className="space-y-1">
              {course.issues.slice(0, 2).map((issue, index) => (
                <div key={index} className="text-xs text-gray-700 bg-gray-50 px-2 py-1">
                  {issue.length > 60 ? `${issue.substring(0, 60)}...` : issue}
                </div>
              ))}
            </div>
            {course.issues.length > 2 && (
              <div className="text-xs text-gray-500 mt-1">
                +{course.issues.length - 2} more issues
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
          <button 
            onClick={onViewDetails}
            className="flex-1 text-xs py-2 px-3 bg-gray-900 text-white hover:bg-gray-700 transition-colors"
          >
            View Analysis
          </button>
          <button className="p-2 hover:bg-gray-100 transition-colors">
            <ExternalLink className="w-3 h-3 text-gray-500" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;