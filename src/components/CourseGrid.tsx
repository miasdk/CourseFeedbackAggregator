import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CourseCard from './CourseCard';
import { X, Star, Users, BookOpen, Download, Filter, MessageCircle } from 'lucide-react';

import { ActionItem, CourseIssueAnalysis } from '../services/issueAnalysis';

export interface Course {
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
  // Smart Filtering Extensions
  issueAnalysis?: CourseIssueAnalysis;
  actionItems?: ActionItem[];
  issueCategories?: string[]; // Categories of issues found
  priorityLevel?: 'urgent' | 'high' | 'medium' | 'low';
}

interface Review {
  reviewer: {
    response_id: string;
    first_name: string;
    last_name: string;
    email: string;
    completion_time: string;
    time_taken: string;
  };
  course_name: string;
  module_name: string;
  rating: number;
  positive_comments: string;
  improvement_opportunities: string;
  is_show_stopper: boolean;
  show_stopper_details?: string | null;
  attachments?: string | null;
  review_date: string;
}

interface CourseGridProps {
  courses: Course[];
}

// Utility function to map course titles to directory names (matches App.tsx)
const getCourseDirectoryName = (courseTitle: string): string => {
  // Create exact mappings for known problematic names
  const exactMappings: { [key: string]: string } = {
    'Transformative Leadership 1.0 and 2.0 Continued': 'Transformative_Leadership_10_and_20_Continued',
    'Transformative Leadership 1.0 and 2.0': 'Transformative_Leadership_10_and_20',
    'Women in Leadership in the Age of AI 1.0 and Women in Leadership in the Age of AI 2.0': 'Women_in_Leadership_in_the_Age_of_AI_10_and_Women_in_Leadership_in_the_Age_of_AI_20',
    'Navigating AI 1.0 and Women in Leadership in the Age of AI 2.0': 'Navigating_AI_10_and_Women_in_Leadership_in_the_Age_of_AI_20',
    'Women in Leadership in the Age of AI 1.0': 'Women_in_Leadership_in_the_Age_of_AI_10',
    'Women in Leadership in the Age of AI 2.0': 'Women_in_Leadership_in_the_Age_of_AI_20',
    'Women in Leadership in the Age of AI 1.0/2.0': 'Women_in_Leadership_in_the_Age_of_AI_1020',
    'Transformative Leadership in Disruptive Times 1.0': 'Transformative_Leadership_in_Disruptive_Times_10',
    'Transformative Leadership in Disruptive Times 2.0': 'Transformative_Leadership_in_Disruptive_Times_20',
    'Transformative Leadership Leading for the Future 1.0': 'Transformative_Leadership_Leading_for_the_Future_10',
    'Transformative Leadership Leading for the Future 2.0': 'Transformative_Leadership_Leading_For_The_Future_20',
    'Transformative Leadership- Leading for the Future 2.0': 'Transformative_Leadership_Leading_For_The_Future_20',
    'Transformative Leadership Leading For The Future 1.0': 'Transformative_Leadership_Leading_For_The_Future_1',
    'Transformative Leadership Leading For The Future 2.0': 'Transformative_Leadership_Leading_For_The_Future_20',
    'Transformative Leadership Leading for the Future 1.0 and 2.0.': 'Transformative_Leadership_Leading_for_the_Future_10_and_20',
    'Transformative-Leadership-Leading-For-The-Future-1': 'Transformative_Leadership_Leading_For_The_Future_1',
    'UC Santa Barbara - Customer Experience Program + Ultimate Toolkit 2024': 'UC_Santa_Barbara_Customer_Experience_Program_Ultimate_Toolkit_2024',
    'Review Team University of San Francisco - Women in Leadership Program + Ultimate Toolkit 2024': 'Review_Team_University_of_San_Francisco_Women_in_Leadership_Program_Ultimate_Toolkit_2024',
    'Women in Leadership Program + Ultimate Toolkit 2024': 'Women_in_Leadership_Program_Ultimate_Toolkit_2024',
    'Customer experience in Healthcare: Revolutionizing Pateint-Centric Care': 'Customer_experience_in_Healthcare_Revolutionizing_Pateint_Centric_Care',
    'Strategic AI for HR Professionals': 'Strategic_AI_for_HR_Professionals',
    'Design Thinking Fundamentals': 'Design_Thinking',
    'Design Thinking': 'Design_Thinking',
    'Customer Experience in Healthcare': 'Customer_experience_in_Healthcare_Revolutionizing_Pateint_Centric_Care',
    'Women in Leadership in the Age of AI': 'Women_in_Leadership_in_the_Age_of_AI',
    'Transformative Leadership in Disruptive Times': 'Transformative_Leadership_in_Disruptive_Times',
    'Transformative Leadership': 'Transformative_Leadership',
    'Generative AI for Value Creation': 'Generative_AI_for_Value_Creation',
    'Strategic AI': 'Strategic_AI',
    'IT and Cybersecurity Leadership': 'IT_and_Cybersecurity_Leadership',
    'Sustainability & AI': 'Sustainability_AI',
    'CX2.0': 'CX20',
    'section 1.0': 'section_10',
    'The Why of AI - Generative AI to Drive Organizational Value and Leadership Transformation': 'The_Why_of_AI_Generative_AI_to_Drive_Organizational_Value_and_Leadership_Transformation',
    'Transformative Leadership - Leading for the Future 1': 'Transformative_Leadership_Leading_For_The_Future_1'
  };

  // Check for exact match first
  if (exactMappings[courseTitle]) {
    return exactMappings[courseTitle];
  }

  // General transformation rules
  let directoryName = courseTitle
    // Handle version numbers: "1.0" -> "10", "2.0" -> "20", etc.
    .replace(/(\d)\.0/g, '$10')
    // Remove special characters except hyphens and underscores
    .replace(/[^\w\s-]/g, '')
    // Replace spaces with underscores
    .replace(/\s+/g, '_')
    // Handle multiple underscores
    .replace(/_+/g, '_')
    // Remove trailing underscores
    .replace(/^_+|_+$/g, '');

  return directoryName;
};

// Function to load reviews for a specific course
const loadCourseReviews = async (courseTitle: string): Promise<Review[]> => {
  try {
    const directoryName = getCourseDirectoryName(courseTitle);
    console.log(`Loading reviews for: ${courseTitle} from directory: ${directoryName}`);
    const response = await fetch(`/courses/${directoryName}/reviews.json`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    let text = await response.text();
    // Replace NaN values with null for valid JSON
    text = text.replace(/:\s*NaN/g, ': null');
    const reviews = JSON.parse(text);
    console.log(`Loaded ${reviews.length} reviews for ${courseTitle}`);
    return Array.isArray(reviews) ? reviews : [];
  } catch (error) {
    console.error(`Failed to load reviews for ${courseTitle}:`, error);
    return [];
  }
};

// Course Details Modal Component with Reviews
const CourseDetailsModal: React.FC<{
  course: Course;
  isOpen: boolean;
  onClose: () => void;
}> = ({ course, isOpen, onClose }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState<'rating' | 'date' | 'reviewer' | 'module'>('rating');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterRating, setFilterRating] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen && course) {
      loadReviews();
    }
  }, [isOpen, course]);

  const loadReviews = async () => {
    setLoading(true);
    try {
      const reviewData = await loadCourseReviews(course.title);
      setReviews(reviewData);
    } catch (error) {
      console.error('Error loading reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const exportData = {
      course: course,
      reviews: filteredAndSortedReviews,
      exportDate: new Date().toISOString(),
      totalReviews: reviews.length,
      averageRating: reviews.length > 0 
        ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length
        : 0
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${course.title.replace(/\s+/g, '_')}_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const filteredAndSortedReviews = reviews
    .filter(review => filterRating === null || review.rating === filterRating)
    .sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'rating':
          aValue = a.rating;
          bValue = b.rating;
          break;
        case 'date':
          aValue = new Date(a.review_date).getTime();
          bValue = new Date(b.review_date).getTime();
          break;
        case 'reviewer':
          aValue = `${a.reviewer.first_name} ${a.reviewer.last_name}`.toLowerCase();
          bValue = `${b.reviewer.first_name} ${b.reviewer.last_name}`.toLowerCase();
          break;
        case 'module':
          aValue = a.module_name;
          bValue = b.module_name;
          break;
        default:
          return 0;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

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

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getShowStopperColor = (isShowStopper: boolean) => {
    return isShowStopper ? 'text-red-600' : 'text-green-600';
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-3xl shadow-apple-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-white border-b border-apple-200 p-6 flex items-center justify-between shrink-0">
              <div>
                <h2 className="text-2xl font-semibold text-apple-900">{course.title}</h2>
                <p className="text-apple-600 mt-1">{course.instructor}</p>
              </div>
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-full hover:bg-apple-100 flex items-center justify-center transition-colors"
              >
                <X className="w-6 h-6 text-apple-600" />
              </button>
            </div>

            {/* Content - Scrollable */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6 space-y-6">
                {/* Course Overview */}
                <div className="flex items-center space-x-8">
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-1">
                      {renderStars(course.rating)}
                    </div>
                    <span className="text-xl font-bold text-apple-900">
                      {course.rating.toFixed(1)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-1 text-apple-600">
                    <Users className="w-5 h-5" />
                    <span>{course.reviewCount} reviews</span>
                  </div>
                  <div className="flex items-center space-x-1 text-apple-600">
                    <BookOpen className="w-5 h-5" />
                    <span>{course.moduleCount} modules</span>
                  </div>
                  <div className="flex items-center space-x-1 text-apple-600">
                    <MessageCircle className="w-5 h-5" />
                    <span>{reviews.length} detailed reviews</span>
                  </div>
                </div>

                {/* Reviews Section */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-apple-900">
                      Course Reviews ({filteredAndSortedReviews.length})
                    </h3>
                    
                    {/* Review Controls */}
                    <div className="flex items-center space-x-4">
                      {/* Rating Filter */}
                      <div className="flex items-center space-x-2">
                        <Filter className="w-4 h-4 text-apple-600" />
                        <select
                          value={filterRating || 'all'}
                          onChange={(e) => setFilterRating(e.target.value === 'all' ? null : parseInt(e.target.value))}
                          className="text-sm border border-apple-200 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="all">All Ratings</option>
                          <option value="5">5 Stars</option>
                          <option value="4">4 Stars</option>
                          <option value="3">3 Stars</option>
                          <option value="2">2 Stars</option>
                          <option value="1">1 Star</option>
                        </select>
                      </div>

                      {/* Sort Controls */}
                      <div className="flex items-center space-x-2">
                        <select
                          value={sortBy}
                          onChange={(e) => setSortBy(e.target.value as any)}
                          className="text-sm border border-apple-200 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="rating">Rating</option>
                          <option value="date">Date</option>
                          <option value="reviewer">Reviewer</option>
                          <option value="module">Module</option>
                        </select>
                        <button
                          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                          className="text-sm px-3 py-1 border border-apple-200 rounded-lg hover:bg-apple-50 transition-colors"
                        >
                          {sortOrder === 'asc' ? '↑' : '↓'}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Reviews List */}
                  {loading ? (
                    <div className="flex items-center justify-center py-8">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full"
                      />
                      <span className="ml-3 text-apple-600">Loading reviews...</span>
                    </div>
                  ) : filteredAndSortedReviews.length === 0 ? (
                    <div className="text-center py-8 text-apple-500">
                      No reviews found for this course.
                    </div>
                  ) : (
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {filteredAndSortedReviews.map((review, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="bg-apple-50 rounded-xl p-4 space-y-3"
                        >
                          {/* Review Header */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="flex items-center space-x-1">
                                {renderStars(review.rating)}
                              </div>
                              <span className="font-semibold text-apple-900">
                                {review.reviewer.first_name} {review.reviewer.last_name}
                              </span>
                              <span className="text-apple-600 text-sm">
                                • {review.module_name}
                              </span>
                            </div>
                            <div className="flex items-center space-x-3">
                              <span className="text-sm text-apple-600">
                                {formatDate(review.review_date)}
                              </span>
                                                             {review.is_show_stopper === true && (
                                 <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">
                                   Show Stopper
                                 </span>
                               )}
                            </div>
                          </div>

                          {/* Review Content */}
                          <div className="space-y-2">
                            {review.positive_comments && (
                              <div>
                                <h5 className="text-sm font-medium text-green-700 mb-1">Positive Comments:</h5>
                                <p className="text-sm text-apple-700 bg-white rounded-lg p-3">
                                  {review.positive_comments}
                                </p>
                              </div>
                            )}
                            
                            {review.improvement_opportunities && (
                              <div>
                                <h5 className="text-sm font-medium text-orange-700 mb-1">Improvement Opportunities:</h5>
                                <p className="text-sm text-apple-700 bg-white rounded-lg p-3">
                                  {review.improvement_opportunities}
                                </p>
                              </div>
                            )}

                                                         {review.is_show_stopper === true && review.show_stopper_details && review.show_stopper_details !== 'null' && review.show_stopper_details.trim() !== '' && (
                               <div>
                                 <h5 className="text-sm font-medium text-red-700 mb-1">Show Stopper Details:</h5>
                                 <p className="text-sm text-red-700 bg-red-50 rounded-lg p-3">
                                   {review.show_stopper_details}
                                 </p>
                               </div>
                             )}

                             {review.attachments && review.attachments !== 'null' && (
                               <div className="flex items-center space-x-2 text-sm text-blue-600">
                                 <Download className="w-4 h-4" />
                                 <span>Attachment: {review.attachments}</span>
                               </div>
                             )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Actions - Fixed Bottom */}
            <div className="bg-white border-t border-apple-200 p-6 flex items-center justify-between shrink-0">
              <div className="text-sm text-apple-600">
                {reviews.length} total reviews • Average rating: {reviews.length > 0 
                  ? (reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length).toFixed(1)
                  : 'N/A'}
              </div>
              <div className="flex items-center space-x-3">
                <button 
                  onClick={handleExport}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Export Report</span>
                </button>
                <button onClick={onClose} className="btn-primary">
                  Close
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

const CourseGrid: React.FC<CourseGridProps> = ({ courses }) => {
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  const handleCourseClick = (course: Course) => {
    setSelectedCourse(course);
  };

  const handleCloseModal = () => {
    setSelectedCourse(null);
  };

  if (courses.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 text-apple-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-apple-900 mb-2">No courses found</h3>
        <p className="text-apple-600">Try adjusting your search or filters to find courses.</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course, index) => (
          <motion.div
            key={course.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <CourseCard 
              course={course} 
              onViewDetails={() => handleCourseClick(course)}
            />
          </motion.div>
        ))}
      </div>

      {/* Course Details Modal */}
      {selectedCourse && (
        <CourseDetailsModal
          course={selectedCourse}
          isOpen={!!selectedCourse}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
};

export default CourseGrid; 