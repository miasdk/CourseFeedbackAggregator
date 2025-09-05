import React from 'react';
import { Search, Upload, Bell, ChevronDown, Settings } from 'lucide-react';
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
      className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm"
    >
      <div className="px-4 py-2">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-7 h-7 bg-blue-600 rounded-sm flex items-center justify-center">
              <span className="text-white font-bold text-sm">CF</span>
            </div>
          </div>

          {/* Search & Controls */}
          <div className="flex items-center space-x-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search courses..."
                className="pl-9 pr-4 py-1.5 w-64 bg-gray-50 border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
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
                  onSortChange(newSortBy);
                }}
                className="appearance-none bg-gray-50 border border-gray-200 rounded px-3 py-1.5 pr-8 focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm min-w-[130px]"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 pointer-events-none" />
            </div>

            {/* Configure Weights Button */}
            <button className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors">
              <Settings className="w-4 h-4" />
              <span>Configure</span>
            </button>

            {/* Upload Button */}
            <button
              onClick={onUploadClick}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              <Upload className="w-4 h-4" />
              <span>Import</span>
            </button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header; 