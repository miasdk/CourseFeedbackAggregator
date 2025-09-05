import React from 'react';
import { Star, Calendar, Users, BookOpen, AlertTriangle, MoreHorizontal } from 'lucide-react';
import { Course } from '../types';

interface CourseCardProps {
  course: Course;
  onViewDetails?: () => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onViewDetails }) => {
  // Removed emoji function - no longer needed

  const getCategoryColor = (category: string) => {
    // Muted professional colors
    return 'bg-gray-100 text-gray-700';
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 ${
          i < Math.floor(rating) 
            ? 'text-gray-900 fill-gray-900' 
            : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <div className="border border-gray-200 bg-white p-4 h-full hover:border-gray-300 transition-colors cursor-pointer">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            {renderStars(course.rating)}
          </div>
          <span className="text-sm font-semibold text-gray-900">
            {course.rating.toFixed(1)}
          </span>
        </div>
        
        <button className="w-6 h-6 hover:bg-gray-100 flex items-center justify-center transition-colors">
          <MoreHorizontal className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      {/* Course Title */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3 line-clamp-2 leading-tight">
        {course.title}
      </h3>

      {/* Category Badge */}
      <div className="mb-3">
        <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-gray-100 text-gray-700">
          {course.category}
        </span>
      </div>

      {/* Description */}
      {course.description && (
        <p className="text-gray-600 text-xs mb-3 line-clamp-2 leading-relaxed">
          {course.description}
        </p>
      )}

      {/* Stats */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>Updated {course.lastUpdated}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Users className="w-3 h-3" />
            <span>{course.reviewCount} reviews</span>
          </div>
          <div className="flex items-center gap-1">
            <BookOpen className="w-3 h-3" />
            <span>{course.moduleCount} modules</span>
          </div>
        </div>

        {/* Critical Issues */}
        {course.criticalIssues > 0 && (
          <div className="flex items-center gap-2 p-2 border border-gray-300">
            <AlertTriangle className="w-3 h-3 text-gray-700" />
            <span className="text-gray-900 text-xs font-medium">
              {course.criticalIssues} critical issue{course.criticalIssues > 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-3 border-t border-gray-200">
        <button 
          onClick={onViewDetails}
          className="flex-1 text-xs py-2 px-3 bg-gray-900 text-white hover:bg-gray-700 transition-colors"
        >
          View Details
        </button>
        <button 
          onClick={() => {
            const exportData = {
              course: course,
              exportDate: new Date().toISOString()
            };
            const dataStr = JSON.stringify(exportData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${course.title.replace(/\s+/g, '_')}_summary.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }}
          className="px-3 py-2 text-xs border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors"
        >
          Export
        </button>
      </div>
    </div>
  );
};

export default CourseCard; 