import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

export function useCourses() {
  const [courses, setCourses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCourses = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('🔄 Fetching courses from API...');
      const data = await apiClient.getCourses();
      console.log(`✅ Fetched ${data.length} courses:`, data.slice(0, 3).map(c => c.course_name));
      setCourses(data);
    } catch (err) {
      console.error('❌ Failed to fetch courses:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch courses');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  return {
    courses,
    isLoading,
    error,
    refetchCourses: fetchCourses
  };
}