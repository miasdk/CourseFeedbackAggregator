import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CourseGrid from './components/CourseGrid';
import PriorityRecommendations from './components/PriorityRecommendations';
import UploadModal from './components/UploadModal';
import APIService, { Feedback, Priority, Stats } from './services/api';

export interface Course {
  id: string;
  title: string;
  category: string;
  rating: number;
  reviewCount: number;
  moduleCount: number;
  lastUpdated: string;
  lastUpdatedDate: Date;
  criticalIssues: number;
  description?: string;
  instructor?: string;
  duration?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  issues?: string[];
  priorityLevel?: 'urgent' | 'high' | 'medium' | 'low';
  analyticsData?: {
    averageRating: number;
    totalReviews: number;
    issueCount: number;
    quickWinPotential: number;
    priorityScore: number;
    tags: string[];
    lastUpdated: string;
  };
}

function App() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [sortBy, setSortBy] = useState<'rating' | 'date' | 'issues' | 'name'>('rating');

  // Load data from API
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [feedbackData, prioritiesData, statsData] = await Promise.all([
          APIService.getFeedback(),
          APIService.getPriorities(), 
          APIService.getStats()
        ]);

        // Convert feedback to courses format for our shadcn components
        const courseMap = new Map<string, Course>();
        
        feedbackData.forEach((item, index) => {
          const courseId = item.id || `course_${index}`;
          if (!courseMap.has(courseId)) {
            const lastUpdatedStr = item.date || '2025-08-29';
            courseMap.set(courseId, {
              id: courseId,
              title: item.course_name,
              category: getCategoryFromName(item.course_name),
              rating: item.rating,
              reviewCount: item.students_affected || 15,
              moduleCount: Math.floor(Math.random() * 8) + 4,
              lastUpdated: lastUpdatedStr,
              lastUpdatedDate: new Date(lastUpdatedStr),
              criticalIssues: item.issues.filter(issue => 
                issue.toLowerCase().includes('critical') || 
                issue.toLowerCase().includes('urgent') ||
                issue.toLowerCase().includes('broken')
              ).length,
              description: `${item.course_name} course with ${item.issues.length} reported issues`,
              instructor: `Dr. ${item.course_name.split(' ')[0]}`,
              duration: `${Math.floor(Math.random() * 12) + 4} weeks`,
              priority: mapPriorityLevel(item.priority),
              priorityLevel: mapToPriorityLevel(item.priority),
              issues: item.issues,
              analyticsData: {
                averageRating: item.rating,
                totalReviews: item.students_affected || 15,
                issueCount: item.issues.length,
                quickWinPotential: item.effort_score ? (10 - item.effort_score) : Math.random() * 10,
                priorityScore: item.total_score || Math.random() * 10,
                tags: item.issues.slice(0, 3),
                lastUpdated: lastUpdatedStr
              }
            });
          }
        });

        setCourses(Array.from(courseMap.values()));
        setPriorities(prioritiesData);
        setStats(statsData);
      } catch (error) {
        console.error('Error loading data:', error);
        // Fallback to empty data
        setCourses([]);
        setPriorities([]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const getCategoryFromName = (name: string): string => {
    const nameLower = name.toLowerCase();
    if (nameLower.includes('ai') || nameLower.includes('artificial')) return 'AI/ML';
    if (nameLower.includes('leadership') || nameLower.includes('transformative')) return 'Leadership';
    if (nameLower.includes('design') || nameLower.includes('ux')) return 'Design';
    if (nameLower.includes('healthcare') || nameLower.includes('health')) return 'Healthcare';
    if (nameLower.includes('strategic') || nameLower.includes('business')) return 'Business';
    if (nameLower.includes('customer') || nameLower.includes('experience')) return 'Customer Experience';
    if (nameLower.includes('sustainability')) return 'Sustainability';
    return 'Technology';
  };

  const mapPriorityLevel = (priority: string): 'low' | 'medium' | 'high' | 'critical' => {
    switch (priority?.toLowerCase()) {
      case 'urgent': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'low';
    }
  };

  const mapToPriorityLevel = (priority: string): 'urgent' | 'high' | 'medium' | 'low' => {
    switch (priority?.toLowerCase()) {
      case 'urgent': 
      case 'critical': return 'urgent';
      case 'high': return 'high';
      case 'medium': return 'medium';
      default: return 'low';
    }
  };

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
  };

  const handleSortChange = (newSort: 'rating' | 'date' | 'issues' | 'name') => {
    setSortBy(newSort);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onUploadClick={() => setIsUploadModalOpen(true)}
        searchQuery={searchQuery}
        onSearchChange={handleSearchChange}
        sortBy={sortBy}
        onSortChange={handleSortChange}
      />
      
      <div className="flex">
        <Sidebar 
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategorySelect}
          courses={courses}
        />
        
        <main className="flex-1 p-6 ml-64">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <PriorityRecommendations />
            
            <div className="mt-8">
              <CourseGrid
                courses={courses}
              />
            </div>
          </motion.div>
        </main>
      </div>

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
      />
      
    </div>
  );
}

export default App;