import React from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  BookOpen, 
  FolderOpen, 
  Brain, 
  Users, 
  PieChart, 
  Heart, 
  Upload,
  Settings,
  Target,
  MessageSquare,
  TrendingUp,
  Database
} from 'lucide-react';
import { Course } from '../types';

interface MenuItemProps {
  icon: React.ReactNode;
  label: string;
  count?: number;
  active?: boolean;
  onClick?: () => void;
}

interface SidebarProps {
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  courses: Course[];
}

const Sidebar: React.FC<SidebarProps> = ({ selectedCategory, onCategoryChange, courses }) => {
  const getCategoryCount = (category: string) => {
    if (category === 'all') return courses.length;
    return courses.filter(course => course.category === category).length;
  };

  const menuItems: MenuItemProps[] = [
    { 
      icon: <Target className="w-5 h-5" />, 
      label: 'Priority Queue', 
      active: selectedCategory === 'all',
      onClick: () => onCategoryChange('all')
    },
    { 
      icon: <MessageSquare className="w-5 h-5" />, 
      label: 'Feedback Sources', 
      count: getCategoryCount('all'),
      active: selectedCategory === 'all',
      onClick: () => onCategoryChange('all')
    },
  ];

  const categoryItems: MenuItemProps[] = [
    { 
      icon: <Brain className="w-5 h-5" />, 
      label: 'AI/ML', 
      count: getCategoryCount('AI/ML'),
      active: selectedCategory === 'AI/ML',
      onClick: () => onCategoryChange('AI/ML')
    },
    { 
      icon: <Users className="w-5 h-5" />, 
      label: 'Leadership', 
      count: getCategoryCount('Leadership'),
      active: selectedCategory === 'Leadership',
      onClick: () => onCategoryChange('Leadership')
    },
    { 
      icon: <PieChart className="w-5 h-5" />, 
      label: 'Design', 
      count: getCategoryCount('Design'),
      active: selectedCategory === 'Design',
      onClick: () => onCategoryChange('Design')
    },
    { 
      icon: <Heart className="w-5 h-5" />, 
      label: 'Healthcare', 
      count: getCategoryCount('Healthcare'),
      active: selectedCategory === 'Healthcare',
      onClick: () => onCategoryChange('Healthcare')
    },
    { 
      icon: <Users className="w-4 h-4" />, 
      label: 'Customer Experience', 
      count: getCategoryCount('Customer Experience'),
      active: selectedCategory === 'Customer Experience',
      onClick: () => onCategoryChange('Customer Experience')
    },
    { 
      icon: <BookOpen className="w-4 h-4" />, 
      label: 'Technology', 
      count: getCategoryCount('Technology'),
      active: selectedCategory === 'Technology',
      onClick: () => onCategoryChange('Technology')
    },
  ];

  const recentItems: MenuItemProps[] = [
    { icon: <Upload className="w-4 h-4" />, label: 'Latest Upload' },
    { icon: <FolderOpen className="w-4 h-4" />, label: 'Recent Analysis' },
  ];

  return (
    <motion.aside 
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="fixed left-0 top-14 h-full w-64 bg-white border-r border-apple-200 shadow-apple overflow-y-auto"
    >
      <div className="p-6">
        {/* Main Navigation */}
        <nav className="space-y-2">
          {menuItems.map((item, index) => (
            <MenuItem key={index} {...item} />
          ))}
        </nav>

        {/* Categories Section */}
        <div className="mt-8">
          <h3 className="text-xs font-medium text-apple-500 uppercase tracking-wider mb-3">
            Categories
          </h3>
          <nav className="space-y-1">
            {categoryItems.map((item, index) => (
              <MenuItem key={index} {...item} />
            ))}
          </nav>
        </div>

        {/* Data Sources */}
        <div className="mt-8">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
            Data Sources
          </h3>
          <nav className="space-y-1">
            <MenuItem 
              icon={<Database className="w-4 h-4" />}
              label="Canvas LMS"
              count={127}
            />
            <MenuItem 
              icon={<TrendingUp className="w-4 h-4" />}
              label="Zoho Surveys"
              count={43}
            />
          </nav>
        </div>

        {/* Settings */}
        <div className="mt-8 pt-8 border-t border-apple-200">
          <MenuItem 
            icon={<Settings className="w-5 h-5" />}
            label="Settings"
          />
        </div>
      </div>
    </motion.aside>
  );
};

const MenuItem: React.FC<MenuItemProps> = ({ icon, label, count, active = false, onClick }) => {
  return (
    <motion.button
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left transition-all duration-200 ${
        active
          ? 'bg-blue-50 text-blue-700 border border-blue-200'
          : 'text-apple-600 hover:bg-apple-100 hover:text-apple-900'
      }`}
    >
      <div className="flex items-center space-x-3">
        {icon}
        <span className="font-medium">{label}</span>
      </div>
      {count !== undefined && count > 0 && (
        <span className={`text-xs px-2 py-1 rounded-full ${
          active 
            ? 'bg-blue-200 text-blue-800' 
            : 'bg-apple-200 text-apple-700'
        }`}>
          {count}
        </span>
      )}
    </motion.button>
  );
};

export default Sidebar; 