import React from 'react';
import { motion } from 'framer-motion';
import { Star, Calendar, Users, BookOpen, AlertTriangle, MoreHorizontal } from 'lucide-react';
import { Course } from './CourseGrid';

interface CourseCardProps {
  course: Course;
  onViewDetails?: () => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onViewDetails }) => {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'AI/ML':
        return '🤖';
      case 'Leadership':
        return '👥';
      case 'Design':
        return '🎨';
      case 'Healthcare':
        return '🏥';
      case 'Technology':
        return '💻';
      default:
        return '📚';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'AI/ML':
        return 'bg-blue-100 text-blue-800';
      case 'Leadership':
        return 'bg-purple-100 text-purple-800';
      case 'Design':
        return 'bg-pink-100 text-pink-800';
      case 'Healthcare':
        return 'bg-green-100 text-green-800';
      case 'Technology':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-apple-100 text-apple-800';
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }).map((_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating) 
            ? 'text-yellow-400 fill-current' 
            : 'text-apple-300'
        }`}
      />
    ));
  };

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="card-apple card-apple-hover p-6 h-full cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getCategoryIcon(course.category)}</span>
          <div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                {renderStars(course.rating)}
              </div>
              <span className="text-lg font-bold text-apple-900">
                {course.rating.toFixed(1)}
              </span>
            </div>
          </div>
        </div>
        
        <button className="w-8 h-8 rounded-full hover:bg-apple-100 flex items-center justify-center transition-colors duration-200">
          <MoreHorizontal className="w-5 h-5 text-apple-600" />
        </button>
      </div>

      {/* Course Title */}
      <h3 className="text-lg font-semibold text-apple-900 mb-2 line-clamp-2">
        {course.title}
      </h3>

      {/* Category Badge */}
      <div className="mb-4">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(course.category)}`}>
          {course.category}
        </span>
      </div>

      {/* Description */}
      {course.description && (
        <p className="text-apple-600 text-sm mb-4 line-clamp-2">
          {course.description}
        </p>
      )}

      {/* Stats */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-1 text-apple-600">
            <Calendar className="w-4 h-4" />
            <span>Updated {course.lastUpdated}</span>
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-1 text-apple-600">
            <Users className="w-4 h-4" />
            <span>{course.reviewCount} reviews</span>
          </div>
          <div className="flex items-center space-x-1 text-apple-600">
            <BookOpen className="w-4 h-4" />
            <span>{course.moduleCount} modules</span>
          </div>
        </div>

        {/* Critical Issues */}
        {course.criticalIssues > 0 && (
          <div className="flex items-center space-x-2 p-2 bg-red-50 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-red-700 text-sm font-medium">
              {course.criticalIssues} critical issue{course.criticalIssues > 1 ? 's' : ''}
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-2 pt-4 border-t border-apple-200">
        <button 
          onClick={onViewDetails}
          className="btn-primary flex-1 text-sm py-2"
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
          className="btn-secondary px-4 py-2 text-sm"
        >
          Export
        </button>
      </div>
    </motion.div>
  );
};

export default CourseCard; 