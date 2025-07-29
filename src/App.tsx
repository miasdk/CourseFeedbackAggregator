import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Filter } from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CourseGrid from './components/CourseGrid';
import PriorityDashboard from './components/StatsCards';
import UploadModal from './components/UploadModal';
import SmartFilters from './components/SmartFilters';
import { IssueAnalysisService } from './services/issueAnalysis';

// Import Course interface from CourseGrid
import { Course } from './components/CourseGrid';

function App() {
  // State management
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState<'rating' | 'date' | 'issues' | 'name'>('rating');
  
  // Smart Filtering State
  const [selectedIssueCategories, setSelectedIssueCategories] = useState<string[]>([]);
  const [selectedPriorityLevels, setSelectedPriorityLevels] = useState<string[]>([]);
  const [selectedActionStatus, setSelectedActionStatus] = useState<string[]>([]);
  const [showOnlyWithActions, setShowOnlyWithActions] = useState(false);
  const [showSmartFilters, setShowSmartFilters] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string>('');

  // Load course data on component mount
  useEffect(() => {
    loadCourseData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Function to map course names to actual directory names
  const mapCourseNameToDirectory = (courseName: string): string => {
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
      'Sustainability & AI': 'Sustainability_AI',
      'CX2.0': 'CX20',
      'section 1.0': 'section_10',
      'The Why of AI - Generative AI to Drive Organizational Value and Leadership Transformation': 'The_Why_of_AI_Generative_AI_to_Drive_Organizational_Value_and_Leadership_Transformation',
      'Transformative Leadership - Leading for the Future 1': 'Transformative_Leadership_Leading_For_The_Future_1'
    };

    // Check for exact match first
    if (exactMappings[courseName]) {
      return exactMappings[courseName];
    }

    // General transformation rules
    let directoryName = courseName
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

  const loadCourseData = async () => {
    try {
      setLoading(true);
      
      // Load the course catalog to get all courses
      const catalogResponse = await fetch('/courses/course_catalog.json');
      if (!catalogResponse.ok) {
        throw new Error('Failed to load course catalog - no sample data available');
      }

      const catalogData = await catalogResponse.json();
      const catalog = catalogData.courses || [];
      console.log(`Loaded course catalog with ${catalog.length} courses and ${catalogData.total_reviews} total reviews`);
      
      // Process all courses from the catalog
      const allCourses: Course[] = [];
      let courseId = 1;
      
      for (const courseEntry of catalog) {
        // Use proper directory mapping
        const directoryName = mapCourseNameToDirectory(courseEntry.name);
        console.log(`Mapping "${courseEntry.name}" -> "${directoryName}"`);
        
        // Load course info
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
          
          // Use data from catalog (which is already calculated)
          const reviewCount = courseEntry.total_reviews || reviews.length;
          const averageRating = courseEntry.average_rating || 
            (reviewCount > 0 ? reviews.reduce((sum: number, review: any) => sum + (review.rating || 0), 0) / reviewCount : 0);
          const criticalIssues = courseEntry.critical_issues || 
            reviews.filter((review: any) => review.is_show_stopper).length;
          
          // Determine category based on course name
          const courseName = courseEntry.name;
          let category = 'Other';
          
          if (courseName.toLowerCase().includes('ai') || courseName.toLowerCase().includes('artificial')) {
            category = 'AI/ML';
          } else if (courseName.toLowerCase().includes('leadership') || courseName.toLowerCase().includes('women in leadership')) {
            category = 'Leadership';
          } else if (courseName.toLowerCase().includes('design')) {
            category = 'Design';
          } else if (courseName.toLowerCase().includes('healthcare') || courseName.toLowerCase().includes('health')) {
            category = 'Healthcare';
          } else if (courseName.toLowerCase().includes('customer') || courseName.toLowerCase().includes('cx')) {
            category = 'Customer Experience';
          } else if (courseName.toLowerCase().includes('sustainability')) {
            category = 'Sustainability';
          } else if (courseName.toLowerCase().includes('cyber') || courseName.toLowerCase().includes('it ') || courseName.toLowerCase().includes('technology')) {
            category = 'Technology';
          } else if (courseName.toLowerCase().includes('consulting')) {
            category = 'Consulting';
          }
          
          // Get latest review date
          const latestReviewDate = reviews.length > 0 
            ? new Date(Math.max(...reviews.map((r: any) => new Date(r.review_date || r.reviewer?.completion_time).getTime())))
            : new Date();
          
          const daysSinceUpdate = Math.floor((Date.now() - latestReviewDate.getTime()) / (1000 * 60 * 60 * 24));
          let lastUpdated = 'No reviews';
          if (reviewCount === 0) lastUpdated = 'No reviews';
          else if (daysSinceUpdate === 0) lastUpdated = 'Today';
          else if (daysSinceUpdate === 1) lastUpdated = '1 day ago';
          else if (daysSinceUpdate < 7) lastUpdated = `${daysSinceUpdate} days ago`;
          else if (daysSinceUpdate < 30) lastUpdated = `${Math.floor(daysSinceUpdate / 7)} week${Math.floor(daysSinceUpdate / 7) > 1 ? 's' : ''} ago`;
          else if (daysSinceUpdate < 365) lastUpdated = `${Math.floor(daysSinceUpdate / 30)} month${Math.floor(daysSinceUpdate / 30) > 1 ? 's' : ''} ago`;
          else lastUpdated = `${Math.floor(daysSinceUpdate / 365)} year${Math.floor(daysSinceUpdate / 365) > 1 ? 's' : ''} ago`;
          
          // Generate action items using smart analysis
          const actionItems = reviews.length > 0 
            ? IssueAnalysisService.generateActionItems(reviews, courseId.toString())
            : [];
          
          // Extract issue categories
          const issueCategories = actionItems.map(item => item.category.id);
          const uniqueCategories = Array.from(new Set(issueCategories));
          
          // Determine priority level based on action items
          let priorityLevel: 'urgent' | 'high' | 'medium' | 'low' = 'low';
          if (actionItems.some(item => item.priority === 'urgent')) priorityLevel = 'urgent';
          else if (actionItems.some(item => item.priority === 'high')) priorityLevel = 'high';
          else if (actionItems.some(item => item.priority === 'medium')) priorityLevel = 'medium';

          const course: Course = {
            id: courseId.toString(),
            title: courseName,
            category: category,
            rating: Math.round(averageRating * 10) / 10,
            reviewCount: reviewCount,
            moduleCount: courseEntry.modules?.length || courseInfo.modules?.length || 1,
            lastUpdated: lastUpdated,
            lastUpdatedDate: latestReviewDate, // Store actual date
            criticalIssues: criticalIssues,
            description: courseInfo.description || `Professional course on ${courseName.toLowerCase()}`,
            instructor: reviews.length > 0 && reviews[0]?.reviewer?.first_name ? 
              `${reviews[0].reviewer.first_name} ${reviews[0].reviewer.last_name}` : 
              'Course Team',
            duration: `${courseEntry.modules?.length || courseInfo.modules?.length || 1} modules`,
            // Smart Filtering Extensions
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
      // NO FALLBACK - only real data as requested
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  // Improved filtering logic - more accurate and consistent
  const applySmartFilters = (coursesToFilter: Course[]): Course[] => {
    return coursesToFilter.filter(course => {
      // Issue category filter - only apply if categories are selected
      if (selectedIssueCategories.length > 0) {
        const hasMatchingCategory = course.issueCategories?.some((cat: string) => 
          selectedIssueCategories.includes(cat)
        );
        if (!hasMatchingCategory) return false;
      }

      // Priority level filter - only apply if priorities are selected
      if (selectedPriorityLevels.length > 0 && course.priorityLevel) {
        if (!selectedPriorityLevels.includes(course.priorityLevel)) {
          return false;
        }
      }

      // Action status filter - improved logic based on actual course data
      if (selectedActionStatus.length > 0) {
        let hasMatchingStatus = false;
        
        // Check for pending actions (courses with issues that need attention)
        if (selectedActionStatus.includes('pending')) {
          if (course.criticalIssues > 0 || (course.actionItems && course.actionItems.length > 0)) {
            hasMatchingStatus = true;
          }
        }
        
        // Check for in-progress (courses being actively worked on - could be based on recent updates)
        if (selectedActionStatus.includes('in-progress')) {
          // Consider courses updated recently as "in progress"
          const daysSinceUpdate = Math.floor((Date.now() - course.lastUpdatedDate.getTime()) / (1000 * 60 * 60 * 24));
          if (daysSinceUpdate <= 30) {
            hasMatchingStatus = true;
          }
        }
        
        // Check for completed/resolved (high-rated courses with few issues)
        if (selectedActionStatus.includes('completed')) {
          if (course.rating >= 4.5 && course.criticalIssues === 0) {
            hasMatchingStatus = true;
          }
        }
        
        if (!hasMatchingStatus) return false;
      }

      // Show only courses with action items - only apply if toggled
      if (showOnlyWithActions) {
        if (!course.actionItems || course.actionItems.length === 0) {
          return false;
        }
      }

      return true;
    });
  };

  // Filter and sort courses based on current state
  const filteredAndSortedCourses = applySmartFilters(courses)
    .filter(course => {
      const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           course.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           course.instructor?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'date':
          return b.lastUpdatedDate.getTime() - a.lastUpdatedDate.getTime();
        case 'issues':
          // Debug logging for issues sorting
          if (process.env.NODE_ENV === 'development') {
            const issuesCount = courses.reduce((acc, course) => {
              acc[course.criticalIssues] = (acc[course.criticalIssues] || 0) + 1;
              return acc;
            }, {} as Record<number, number>);
            console.log('📊 Critical Issues Distribution:', issuesCount);
            console.log(`🎯 Sorting ${courses.length} courses by issues - Top 5:`, 
              courses.sort((x, y) => y.criticalIssues - x.criticalIssues)
                .slice(0, 5)
                .map(c => `${c.title}: ${c.criticalIssues} issues`)
            );
          }
          return b.criticalIssues - a.criticalIssues;
        case 'name':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });

  const handleUploadComplete = (newCourses: Course[]) => {
    setCourses(prev => [...prev, ...newCourses]);
  };

  // Smart Filtering Handlers
  const handleIssueCategoryToggle = (category: string) => {
    setSelectedIssueCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handlePriorityLevelToggle = (priority: string) => {
    setSelectedPriorityLevels(prev => 
      prev.includes(priority) 
        ? prev.filter(p => p !== priority)
        : [...prev, priority]
    );
  };

  const handleActionStatusToggle = (status: string) => {
    setSelectedActionStatus(prev => 
      prev.includes(status) 
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  const handleToggleShowOnlyWithActions = () => {
    setShowOnlyWithActions(prev => !prev);
  };

  const handleClearSmartFilters = () => {
    setSelectedIssueCategories([]);
    setSelectedPriorityLevels([]);
    setSelectedActionStatus([]);
    setShowOnlyWithActions(false);
  };

  // Priority Dashboard Action Handler
  const handlePriorityActionClick = (action: any) => {
    console.log('🎯 Priority Action Clicked:', action.type, 'Courses:', action.courses?.length);
    
    // Show user feedback
    let feedbackMessage = '';
    
    // Clear existing filters first
    handleClearSmartFilters();
    
    // Apply more accurate filters and sorting based on action type
    switch (action.type) {
      case 'urgent':
        setSortBy('issues');
        setSelectedActionStatus(['pending']);
        setShowSmartFilters(true);
        feedbackMessage = `Showing ${action.courses?.length || 0} courses that need urgent attention (sorted by critical issues)`;
        break;
        
      case 'quick-wins':
        setSortBy('rating');
        setSelectedPriorityLevels(['medium', 'low']);
        setShowSmartFilters(true);
        feedbackMessage = `Showing ${action.courses?.length || 0} high-rated courses with easy improvement opportunities`;
        break;
        
      case 'improvement':
        setSortBy('issues');
        setSelectedPriorityLevels(['high', 'medium']);
        setShowSmartFilters(true);
        feedbackMessage = `Showing ${action.courses?.length || 0} courses with significant improvement potential`;
        break;
        
      case 'performing':
        setSortBy('rating');
        setSelectedActionStatus(['completed']);
        setShowSmartFilters(true);
        feedbackMessage = `Showing ${action.courses?.length || 0} top-performing courses (4.5+ stars, minimal issues)`;
        break;
        
      default:
        setShowSmartFilters(true);
        feedbackMessage = 'Smart filters activated';
    }
    
    // Show feedback message
    setActionFeedback(feedbackMessage);
    setTimeout(() => setActionFeedback(''), 4000);
    
    // Scroll to courses section
    setTimeout(() => {
      const coursesElement = document.querySelector('[data-courses-section]');
      if (coursesElement) {
        coursesElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };



  if (loading) {
    return (
      <div className="min-h-screen bg-apple-50 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-apple-50">
      <Header 
        onUploadClick={() => setUploadModalOpen(true)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        sortBy={sortBy}
        onSortChange={setSortBy}
      />
      
      {/* Action Feedback Toast */}
      {actionFeedback && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-20 left-1/2 transform -translate-x-1/2 z-40 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg max-w-md text-center text-sm"
        >
          {actionFeedback}
        </motion.div>
      )}
      
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          courses={courses}
        />
        
        {/* Main Content */}
        <main className="flex-1 ml-64 p-8 pt-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-7xl mx-auto"
          >
            {/* Priority Dashboard */}
            <PriorityDashboard courses={courses} onActionClick={handlePriorityActionClick} />
            
            {/* Smart Filters Toggle */}
            <div className="mt-8">
              <motion.button
                onClick={() => setShowSmartFilters(!showSmartFilters)}
                className="mb-4 flex items-center space-x-2 px-4 py-2 bg-white border border-apple-200 rounded-lg hover:bg-apple-50 transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Filter className="w-4 h-4 text-apple-600" />
                <span className="text-apple-700 font-medium">
                  {showSmartFilters ? 'Hide' : 'Show'} Smart Filters
                </span>
                {(selectedIssueCategories.length > 0 || selectedPriorityLevels.length > 0 || selectedActionStatus.length > 0 || showOnlyWithActions) && (
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
                    Active
                  </span>
                )}
              </motion.button>
            </div>

            {/* Smart Filters */}
            {showSmartFilters && (
              <div data-smart-filters>
                <SmartFilters
                selectedIssueCategories={selectedIssueCategories}
                selectedPriorityLevels={selectedPriorityLevels}
                selectedActionStatus={selectedActionStatus}
                showOnlyWithActions={showOnlyWithActions}
                onIssueCategoryToggle={handleIssueCategoryToggle}
                onPriorityLevelToggle={handlePriorityLevelToggle}
                onActionStatusToggle={handleActionStatusToggle}
                onToggleShowOnlyWithActions={handleToggleShowOnlyWithActions}
                onClearFilters={handleClearSmartFilters}
                filteredCount={filteredAndSortedCourses.length}
                totalCount={courses.length}
              />
              </div>
            )}
            
            {/* Course Grid */}
            <div className="mt-8" data-courses-section>
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-apple-900 mb-2">
                  Course Overview
                </h2>
                <p className="text-apple-600">
                  {filteredAndSortedCourses.length} course{filteredAndSortedCourses.length !== 1 ? 's' : ''} found
                  {searchQuery && ` for "${searchQuery}"`}
                  {selectedCategory !== 'all' && ` in ${selectedCategory}`}
                </p>
              </div>
              
              <CourseGrid courses={filteredAndSortedCourses} />
            </div>
          </motion.div>
        </main>
      </div>

      {/* Upload Modal */}
      <UploadModal 
        isOpen={uploadModalOpen} 
        onClose={() => setUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />
    </div>
  );
}

export default App;
