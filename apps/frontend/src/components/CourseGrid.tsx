import type React from "react"
import CourseCard from "./CourseCard"
import type { Course } from "../types"

interface CourseGridProps {
  courses: Course[]
  onCourseSelect?: (course: Course) => void
}

const CourseGrid: React.FC<CourseGridProps> = ({ courses, onCourseSelect }) => {
  if (courses.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No courses found</h3>
        <p className="text-gray-600">Try adjusting your search or filters to find courses.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          course={course}
          onViewDetails={() => onCourseSelect?.(course)}
        />
      ))}
    </div>
  )
}

export default CourseGrid; 