import { useState, useCallback, useEffect } from "react";
import { toast } from "sonner@2.0.3";

export function useTheme() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if user has a saved preference
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme-preference');
      if (saved) {
        return saved === 'dark';
      }
      // Fall back to system preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  const toggleTheme = useCallback(() => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    
    // Update DOM (only in browser)
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', newTheme);
    }
    
    // Save preference (only in browser)
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('theme-preference', newTheme ? 'dark' : 'light');
    }
    
    toast.info(`Switched to ${newTheme ? 'dark' : 'light'} mode`);
  }, [isDarkMode]);

  // Initialize theme on mount
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDarkMode);
    }
  }, [isDarkMode]);

  // Listen for system theme changes
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      const hasCustomPreference = typeof localStorage !== 'undefined' 
        ? localStorage.getItem('theme-preference') 
        : null;
      if (!hasCustomPreference) {
        setIsDarkMode(e.matches);
        if (typeof document !== 'undefined') {
          document.documentElement.classList.toggle('dark', e.matches);
        }
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return {
    isDarkMode,
    toggleTheme
  };
}