/**
 * Application Constants
 * 
 * Centralized constants for the Course Improvement Prioritization System
 * to ensure consistency across components and easy maintenance.
 */

/** Application metadata */
export const APPLICATION_METADATA = {
  name: 'Course Improvement Prioritization System',
  version: '1.0.0',
  description: 'Executive Education course improvement dashboard with AI-powered prioritization',
  author: 'Course Prioritization Team'
} as const;

/** User interface constants */
export const UI_CONSTANTS = {
  /** Toast notification configuration */
  TOAST_CONFIG: {
    position: 'top-right' as const,
    richColors: true,
    closeButton: true,
    expand: false,
    visibleToasts: 5,
    duration: 4000
  },
  
  /** Search and filtering */
  SEARCH_DEBOUNCE_MS: 300,
  MINIMUM_SEARCH_LENGTH: 2,
  
  /** Animation durations */
  ANIMATION_DURATION: {
    fast: 150,
    normal: 300,
    slow: 500
  },
  
  /** Breakpoints */
  BREAKPOINTS: {
    mobile: 768,
    tablet: 1024,
    desktop: 1280
  }
} as const;

/** Data synchronization constants */
export const DATA_SYNC_CONSTANTS = {
  /** Automatic refresh intervals (in milliseconds) */
  AUTO_REFRESH_INTERVAL: 5 * 60 * 1000, // 5 minutes
  SYNC_TIMEOUT: 30 * 1000, // 30 seconds
  
  /** Retry configuration */
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY_MS: 1000,
  
  /** Batch sizes */
  CANVAS_BATCH_SIZE: 50,
  ZOHO_BATCH_SIZE: 100
} as const;

/** Scoring algorithm constants */
export const SCORING_CONSTANTS = {
  /** Weight validation */
  TOTAL_WEIGHT_REQUIRED: 100,
  MIN_WEIGHT_VALUE: 0,
  MAX_WEIGHT_VALUE: 100,
  
  /** Score ranges */
  SCORE_RANGE: {
    min: 0,
    max: 100
  },
  
  /** Priority thresholds */
  PRIORITY_THRESHOLDS: {
    critical: 90,
    high: 75,
    medium: 50,
    low: 25
  }
} as const;

/** Status and category definitions */
export const STATUS_DEFINITIONS = {
  RECOMMENDATION_STATUSES: [
    { value: 'pending', label: 'Pending Review', color: 'amber' },
    { value: 'validated', label: 'Validated', color: 'green' },
    { value: 'in_progress', label: 'In Progress', color: 'blue' },
    { value: 'completed', label: 'Completed', color: 'emerald' },
    { value: 'dismissed', label: 'Dismissed', color: 'gray' }
  ],
  
  RECOMMENDATION_CATEGORIES: [
    { value: 'content', label: 'Content Quality' },
    { value: 'technical', label: 'Technical Issues' },
    { value: 'user_experience', label: 'User Experience' },
    { value: 'engagement', label: 'Student Engagement' },
    { value: 'accessibility', label: 'Accessibility' },
    { value: 'performance', label: 'Performance' }
  ]
} as const;

/** Error messages */
export const ERROR_MESSAGES = {
  NETWORK: {
    CONNECTION_FAILED: 'Unable to connect to the server. Please check your internet connection.',
    TIMEOUT: 'Request timed out. Please try again.',
    SERVER_ERROR: 'Server error occurred. Please contact support if the issue persists.'
  },
  
  VALIDATION: {
    WEIGHTS_TOTAL: 'Scoring weights must total exactly 100%',
    REQUIRED_FIELD: 'This field is required',
    INVALID_FORMAT: 'Invalid format provided'
  },
  
  DATA_SYNC: {
    CANVAS_SYNC_FAILED: 'Failed to sync Canvas LMS data',
    ZOHO_SYNC_FAILED: 'Failed to sync Zoho CRM data',
    SYNC_IN_PROGRESS: 'Sync already in progress. Please wait.'
  }
} as const;

/** Success messages */
export const SUCCESS_MESSAGES = {
  VALIDATION: {
    RECOMMENDATION_VALIDATED: 'Recommendation has been successfully validated',
    WEIGHTS_UPDATED: 'Scoring weights have been updated successfully',
    SCORES_RECOMPUTED: 'Priority scores have been recomputed with new weights'
  },
  
  DATA_SYNC: {
    CANVAS_SYNCED: 'Canvas LMS data synchronized successfully',
    ZOHO_SYNCED: 'Zoho CRM data synchronized successfully',
    DASHBOARD_REFRESHED: 'Dashboard data has been refreshed'
  }
} as const;

/** API endpoints (for future backend integration) */
export const API_ENDPOINTS = {
  BASE_URL: '/api/v1',
  
  RECOMMENDATIONS: '/recommendations',
  SCORING_WEIGHTS: '/scoring/weights',
  DATA_SOURCES: '/data-sources',
  SYNC: {
    CANVAS: '/sync/canvas',
    ZOHO: '/sync/zoho'
  },
  
  VALIDATION: '/recommendations/:id/validate',
  EXPORT: '/export/recommendations'
} as const;

/** Local storage keys */
export const STORAGE_KEYS = {
  THEME_PREFERENCE: 'cips-theme-preference',
  SCORING_WEIGHTS: 'cips-scoring-weights',
  DASHBOARD_FILTERS: 'cips-dashboard-filters',
  USER_PREFERENCES: 'cips-user-preferences'
} as const;