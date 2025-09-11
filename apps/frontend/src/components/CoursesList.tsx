import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Calendar, Users, AlertTriangle } from "lucide-react";

interface Course {
  course_id: string;
  course_name: string;
  instructor_name?: string;
  status: string;
  start_date?: string;
  end_date?: string;
  feedback_count?: number;
  priority_issues?: number;
}

interface CoursesListProps {
  courses: Course[];
  loading?: boolean;
}

export function CoursesList({ courses, loading = false }: CoursesListProps) {
  // Ensure courses is an array
  const courseList = Array.isArray(courses) ? courses : [];
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not set';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'draft': return 'bg-yellow-100 text-yellow-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-3">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mt-2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (courseList.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="text-center py-16">
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center">
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-medium">No courses found</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                There are no courses available at this time. Try syncing your data sources or check back later.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Results summary */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium">
          All Courses
        </h2>
        <span className="text-sm text-muted-foreground">
          {courseList.length} course{courseList.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* 2-column grid layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {courseList.map((course) => (
          <Card key={course.course_id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  {(course.priority_issues || 0) > 0 && (
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="destructive" className="text-xs">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        {course.priority_issues} issues
                      </Badge>
                    </div>
                  )}
                  <h3 className="font-semibold text-sm leading-tight mb-1">
                    {course.course_name}
                  </h3>
                  {course.instructor_name && (
                    <p className="text-xs text-muted-foreground mb-2">
                      Instructor: {course.instructor_name}
                    </p>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="space-y-3">
                {/* Course dates */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(course.start_date)} - {formatDate(course.end_date)}
                  </div>
                </div>

                {/* Feedback stats */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {course.feedback_count || 0} feedback items
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    View Details
                  </Button>
                  {(course.feedback_count || 0) > 0 && (
                    <Button variant="default" size="sm" className="flex-1">
                      View Feedback
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}