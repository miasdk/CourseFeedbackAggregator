import type React from "react"
import type { Course } from "../types"

interface CourseCardProps {
  course: Course
  onViewDetails?: () => void
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onViewDetails }) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-500 text-white'
      case 'high':
        return 'bg-orange-500 text-white'
      case 'medium':
        return 'bg-amber-500 text-white'
      case 'low':
        return 'bg-emerald-500 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <h3 className="font-semibold text-gray-900 text-lg leading-tight">{course.title}</h3>
          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityBadge(course.priority)}`}>
            {course.priority}
          </span>
        </div>
        
        <div className="text-sm text-gray-600 mb-4">
          {course.category} • {course.instructor || 'No instructor'}
        </div>

        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span>{course.rating.toFixed(1)}/5.0 rating</span>
          <span>{course.reviewCount} reviews</span>
          <span>{course.criticalIssues} critical issues</span>
        </div>

        {course.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {course.description}
          </p>
        )}

        <button
          onClick={onViewDetails}
          className="w-full py-2 px-4 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors"
        >
          View Details
        </button>
      </div>
    </div>
  )
}

export default CourseCard
