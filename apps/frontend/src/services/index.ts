/**
 * Services index - single import point for all services
 */

export * from './api';

// Re-export original API for backward compatibility during migration
import { mockApiClient } from './mockApi';
export { mockApiClient };