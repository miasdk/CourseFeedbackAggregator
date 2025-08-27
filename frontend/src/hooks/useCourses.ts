import { useState, useEffect } from 'react';
import { Course } from '../types/course';
import { mapCourseNameToDirectory, determineCategory, formatLastUpdated } from '../utils/courseHelpers';
import { IssueAnalysisService } from '../services/issueAnalysis';

export const useCourses = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  const loadCourseData = async () => {
    try {
      setLoading(true);
      
      const catalogResponse = await fetch('/courses/course_catalog.json');
      if (!catalogResponse.ok) {
        throw new Error('Failed to load course catalog - no sample data available');
      }

      const catalogData = await catalogResponse.json();
      const catalog = catalogData.courses || [];
      console.log(`Loaded course catalog with ${catalog.length} courses and ${catalogData.total_reviews} total reviews`);
      
      const allCourses: Course[] = [];
      let courseId = 1;
      
      for (const courseEntry of catalog) {
        const directoryName = mapCourseNameToDirectory(courseEntry.name);
        console.log(`Mapping "${courseEntry.name}" -> "${directoryName}"`);
        
        try {
          const courseInfoResponse = await fetch(`/courses/${directoryName}/course_info.json`);
          const reviewsResponse = await fetch(`/courses/${directoryName}/reviews.json`);
          
          let courseInfo: any = {};
          let reviews: any[] = [];
          
          if (courseInfoResponse.ok) {
            courseInfo = await courseInfoResponse.json();
          } else {
            console.warn(`Course info not found for ${directoryName}`);
          }
          
          if (reviewsResponse.ok) {
            let reviewText = await reviewsResponse.text();
            reviewText = reviewText.replace(/:\s*NaN/g, ': null');
            reviews = JSON.parse(reviewText);
            console.log(`Loaded ${reviews.length} reviews for ${courseEntry.name}`);
          } else {
            console.warn(`Reviews not found for ${directoryName}`);
          }
          
          const reviewCount = courseEntry.total_reviews || reviews.length;
          const averageRating = courseEntry.average_rating || 
            (reviewCount > 0 ? reviews.reduce((sum: number, review: any) => sum + (review.rating || 0), 0) / reviewCount : 0);
          const criticalIssues = courseEntry.critical_issues || 
            reviews.filter((review: any) => review.is_show_stopper).length;
          
          const category = determineCategory(courseEntry.name);
          
          const latestReviewDate = reviews.length > 0 
            ? new Date(Math.max(...reviews.map((r: any) => new Date(r.review_date || r.reviewer?.completion_time).getTime())))
            : new Date();
          
          const lastUpdated = formatLastUpdated(latestReviewDate, reviewCount);
          
          const actionItems = reviews.length > 0 
            ? IssueAnalysisService.generateActionItems(reviews, courseId.toString())
            : [];
          
          const issueCategories = actionItems.map(item => item.category.id);
          const uniqueCategories = Array.from(new Set(issueCategories));
          
          let priorityLevel: 'urgent' | 'high' | 'medium' | 'low' = 'low';
          if (actionItems.some(item => item.priority === 'urgent')) priorityLevel = 'urgent';
          else if (actionItems.some(item => item.priority === 'high')) priorityLevel = 'high';
          else if (actionItems.some(item => item.priority === 'medium')) priorityLevel = 'medium';

          const course: Course = {
            id: courseId.toString(),
            title: courseEntry.name,
            category: category,
            rating: Math.round(averageRating * 10) / 10,
            reviewCount: reviewCount,
            moduleCount: courseEntry.modules?.length || courseInfo.modules?.length || 1,
            lastUpdated: lastUpdated,
            lastUpdatedDate: latestReviewDate,
            criticalIssues: criticalIssues,
            description: courseInfo.description || `Professional course on ${courseEntry.name.toLowerCase()}`,
            instructor: reviews.length > 0 && reviews[0]?.reviewer?.first_name ? 
              `${reviews[0].reviewer.first_name} ${reviews[0].reviewer.last_name}` : 
              'Course Team',
            duration: `${courseEntry.modules?.length || courseInfo.modules?.length || 1} modules`,
            actionItems: actionItems,
            issueCategories: uniqueCategories,
            priorityLevel: priorityLevel,
            issueAnalysis: {
              courseId: courseId.toString(),
              totalReviews: reviewCount,
              criticalIssues: criticalIssues,
              actionItems: actionItems,
              issueBreakdown: {},
              lastAnalyzed: new Date()
            }
          };
          
          allCourses.push(course);
          courseId++;
          
        } catch (courseError) {
          console.error(`Failed to load data for course: ${courseEntry.name} (${directoryName})`, courseError);
        }
      }
      
      console.log(`Successfully loaded ${allCourses.length} courses with ${allCourses.reduce((sum, course) => sum + course.reviewCount, 0)} total reviews`);
      setCourses(allCourses);
      
    } catch (error) {
      console.error('Error loading course data:', error);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourseData();
  }, []);

  return { courses, loading, setCourses };
};