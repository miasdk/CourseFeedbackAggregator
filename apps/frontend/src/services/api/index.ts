/**
 * API services index
 * Re-exports all API services for easy importing
 */

export { default as apiClient } from './client';
export * from './courses';
export * from './feedback';
export * from './priorities';
export * from './ingest';
export * from './webhooks';

// Re-export types for convenience
export type {
  IngestRequest,
  IngestResponse,
  JobStatus
} from './ingest';

export type {
  WebhookEvent,
  WebhookStats
} from './webhooks';