import React from 'react';
import { Search, Upload, Bell, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';

interface HeaderProps {
  onUploadClick: () => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortBy: 'rating' | 'date' | 'issues' | 'name';
  onSortChange: (sort: 'rating' | 'date' | 'issues' | 'name') => void;
}

const Header: React.FC<HeaderProps> = ({ 
  onUploadClick, 
  searchQuery, 
  onSearchChange, 
  sortBy, 
  onSortChange 
}) => {
  const sortOptions = [
    { value: 'rating', label: 'Highest Rated' },
    { value: 'date', label: 'Recently Updated' },
    { value: 'issues', label: 'Most Issues' },
    { value: 'name', label: 'Alphabetical' }
  ];

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-lg border-b border-apple-200 shadow-apple"
    >
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-3"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">CA</span>
            </div>
            <div>
              <h1 className="text-xl font-semibold text-apple-900">Course Analyzer</h1>
              <p className="text-xs text-apple-600">Professional Review Platform</p>
            </div>
          </motion.div>

          {/* Search & Controls */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-apple-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search courses, instructors, topics..."
                className="pl-9 pr-4 py-2 w-80 bg-apple-50 border border-apple-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-sm"
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
              />
            </div>

            {/* Sort Dropdown */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => {
                  const newSortBy = e.target.value as typeof sortBy;
                  console.log(`🔄 Sorting changed to: ${newSortBy}`); // Debug log
                  onSortChange(newSortBy);
                }}
                className="appearance-none bg-apple-50 border border-apple-200 rounded-xl px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 text-sm min-w-[140px]"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-apple-400 w-4 h-4 pointer-events-none" />
            </div>

            {/* Notifications */}
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="relative p-2 bg-apple-50 hover:bg-apple-100 rounded-xl transition-colors duration-200"
            >
              <Bell className="w-4 h-4 text-apple-600" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-red-500 rounded-full"></span>
            </motion.button>

            {/* Upload Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onUploadClick}
              className="btn-primary flex items-center space-x-2 px-4 py-2 text-sm"
            >
              <Upload className="w-4 h-4" />
              <span>Upload CSV</span>
            </motion.button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header; 