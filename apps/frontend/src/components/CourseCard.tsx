"use client"

import type React from "react"
import { AlertTriangle, Users, MessageSquare, ExternalLink } from "lucide-react"
import type { Course } from "../types"

interface CourseCardProps {
  course: Course
  onViewDetails?: () => void
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onViewDetails }) => {
  // Calculate priority score (simplified)
  const priorityScore = course.analyticsData?.priorityScore || Math.random() * 10

  const getPriorityStyle = (score: number) => {
    if (score >= 8)
      return {
        color: "text-red-800",
        bg: "bg-gradient-to-r from-red-50 to-red-100",
        border: "border-red-300",
        badge: "bg-red-500 text-white",
        label: "Critical",
      }
    if (score >= 6)
      return {
        color: "text-orange-800",
        bg: "bg-gradient-to-r from-orange-50 to-orange-100",
        border: "border-orange-300",
        badge: "bg-orange-500 text-white",
        label: "High",
      }
    if (score >= 4)
      return {
        color: "text-amber-800",
        bg: "bg-gradient-to-r from-amber-50 to-amber-100",
        border: "border-amber-300",
        badge: "bg-amber-500 text-white",
        label: "Medium",
      }
    return {
      color: "text-emerald-700",
      bg: "bg-gradient-to-r from-emerald-50 to-emerald-100",
      border: "border-emerald-300",
      badge: "bg-emerald-500 text-white",
      label: "Low",
    }
  }

  const priorityStyle = getPriorityStyle(priorityScore)

  // Get feedback summary
  const totalIssues = course.issues?.length || 0
  const studentsAffected = course.reviewCount || 0

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-200 overflow-hidden">
      <div className={`px-6 py-4 ${priorityStyle.bg} ${priorityStyle.border} border-b`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`text-xs font-semibold px-3 py-1 rounded-full ${priorityStyle.badge}`}>
              {priorityStyle.label}
            </div>
            <div className="text-lg font-bold text-gray-900">{priorityScore.toFixed(1)}</div>
          </div>
          {course.criticalIssues > 0 && (
            <div className="flex items-center gap-2 bg-red-100 px-3 py-1 rounded-full">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <span className="text-sm text-red-800 font-semibold">{course.criticalIssues} Critical</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-6">
        <h3 className="font-bold text-gray-900 text-lg mb-3 leading-tight text-balance">{course.title}</h3>

        <div className="mb-4">
          <span className="text-sm text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full font-medium">
            {course.category}
          </span>
        </div>

        <div className="space-y-3 mb-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-gray-600">
              <div className="p-1 bg-blue-100 rounded">
                <MessageSquare className="w-4 h-4 text-blue-600" />
              </div>
              <span className="text-sm font-medium">{totalIssues} issues reported</span>
            </div>
            <div className="flex items-center gap-2 text-gray-600">
              <div className="p-1 bg-purple-100 rounded">
                <Users className="w-4 h-4 text-purple-600" />
              </div>
              <span className="text-sm font-medium">{studentsAffected} students</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className={`w-4 h-4 ${i < Math.floor(course.rating) ? "text-yellow-400" : "text-gray-300"}`}
                >
                  ★
                </div>
              ))}
            </div>
            <span className="text-sm font-semibold text-gray-700">{course.rating.toFixed(1)}/5.0</span>
          </div>
        </div>

        {course.issues && course.issues.length > 0 && (
          <div className="mb-5">
            <div className="text-sm font-semibold text-gray-700 mb-3">Recent Issues:</div>
            <div className="space-y-2">
              {course.issues.slice(0, 2).map((issue, index) => (
                <div
                  key={index}
                  className="text-sm text-gray-700 bg-gray-50 px-4 py-3 rounded-lg border-l-4 border-gray-300"
                >
                  {issue.length > 60 ? `${issue.substring(0, 60)}...` : issue}
                </div>
              ))}
            </div>
            {course.issues.length > 2 && (
              <div className="text-sm text-gray-500 mt-3 font-medium">
                +{course.issues.length - 2} more issues to review
              </div>
            )}
          </div>
        )}

        <div className="flex items-center gap-3 pt-4 border-t border-gray-100">
          <button
            onClick={onViewDetails}
            className="flex-1 text-sm font-semibold py-3 px-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors duration-200 shadow-sm"
          >
            View Analysis
          </button>
          <button className="p-3 hover:bg-gray-100 rounded-lg transition-colors duration-200 border border-gray-200">
            <ExternalLink className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default CourseCard
