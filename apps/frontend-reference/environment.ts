/**
 * Environment Configuration Utilities
 * 
 * Provides safe access to environment variables and configuration
 * that works across different runtime environments.
 */

/**
 * Safe environment variable access
 * Works in both browser and Node.js environments
 */
function getEnvironmentVariable(key: string, defaultValue?: string): string | undefined {
  // Check if we're in a browser environment
  if (typeof window !== 'undefined') {
    // In browser, environment variables are typically injected at build time
    // For now, return the default value
    return defaultValue;
  }
  
  // In Node.js environment, access process.env
  if (typeof process !== 'undefined' && process.env) {
    return process.env[key] || defaultValue;
  }
  
  return defaultValue;
}

/**
 * Application environment configuration
 */
export const ENVIRONMENT_CONFIG = {
  /** API base URL */
  API_BASE_URL: getEnvironmentVariable('REACT_APP_API_URL', '/api/v1'),
  
  /** Application environment */
  NODE_ENV: getEnvironmentVariable('NODE_ENV', 'development'),
  
  /** Feature flags */
  FEATURES: {
    ENABLE_ANALYTICS: getEnvironmentVariable('REACT_APP_ENABLE_ANALYTICS', 'false') === 'true',
    ENABLE_DEBUG_MODE: getEnvironmentVariable('REACT_APP_DEBUG_MODE', 'false') === 'true',
    ENABLE_MOCK_DATA: getEnvironmentVariable('REACT_APP_ENABLE_MOCK_DATA', 'true') === 'true'
  },
  
  /** External service URLs */
  SERVICES: {
    CANVAS_API_URL: getEnvironmentVariable('REACT_APP_CANVAS_API_URL', 'https://canvas.instructure.com/api/v1'),
    ZOHO_API_URL: getEnvironmentVariable('REACT_APP_ZOHO_API_URL', 'https://www.zohoapis.com/crm/v2')
  }
} as const;

/**
 * Check if we're in development mode
 */
export const isDevelopment = (): boolean => {
  return ENVIRONMENT_CONFIG.NODE_ENV === 'development';
};

/**
 * Check if we're in production mode
 */
export const isProduction = (): boolean => {
  return ENVIRONMENT_CONFIG.NODE_ENV === 'production';
};

/**
 * Check if debug mode is enabled
 */
export const isDebugMode = (): boolean => {
  return ENVIRONMENT_CONFIG.FEATURES.ENABLE_DEBUG_MODE || isDevelopment();
};