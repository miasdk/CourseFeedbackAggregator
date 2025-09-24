/**
 * Global application state management with Zustand
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  User,
  AppConfig,
  ConnectionStatus,
  WebSocketEvent,
  LoadingState
} from '../shared/types';
import { webhookApi } from '../services/api/webhooks';
import { ingestApi } from '../services/api/ingest';

interface AppState {
  // User and auth
  user: User | null;
  isAuthenticated: boolean;

  // App configuration
  config: AppConfig;

  // Connection states
  connectionStatus: {
    api: ConnectionStatus;
    webhooks: ConnectionStatus;
    zoho: ConnectionStatus;
    canvas: ConnectionStatus;
  };

  // Real-time features
  liveUpdates: boolean;
  eventStream: EventSource | null;
  recentEvents: WebSocketEvent[];

  // UI State
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  loading: LoadingState;
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: string;
    read: boolean;
  }>;

  // Data source monitoring
  lastWebhookActivity: string | null;
  ingestJobs: Array<{
    id: string;
    source: 'zoho' | 'canvas';
    status: 'pending' | 'running' | 'completed' | 'failed';
    startedAt: string;
    progress: number;
  }>;

  // Actions
  setUser: (user: User | null) => void;
  updateConfig: (config: Partial<AppConfig>) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // Connection monitoring
  checkConnections: () => Promise<void>;
  startLiveUpdates: () => void;
  stopLiveUpdates: () => void;

  // Notifications
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp' | 'read'>) => void;
  markNotificationRead: (id: string) => void;
  clearNotifications: () => void;

  // Data source actions
  testConnection: (service: 'zoho' | 'canvas') => Promise<boolean>;
  triggerManualIngest: (source: 'zoho' | 'canvas', params?: any) => Promise<void>;

  // Error handling
  handleError: (error: Error, context?: string) => void;
}

const defaultConfig: AppConfig = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  enableMockData: import.meta.env.VITE_ENABLE_MOCK_DATA === 'true',
  refreshInterval: 30000, // 30 seconds
  features: {
    webhookMonitoring: true,
    manualIngest: true,
    advancedAnalytics: false,
    realTimeUpdates: true,
  },
};

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        config: defaultConfig,
        connectionStatus: {
          api: 'disconnected',
          webhooks: 'disconnected',
          zoho: 'disconnected',
          canvas: 'disconnected',
        },
        liveUpdates: false,
        eventStream: null,
        recentEvents: [],
        sidebarOpen: true,
        theme: 'system',
        loading: 'idle',
        notifications: [],
        lastWebhookActivity: null,
        ingestJobs: [],

        // Actions
        setUser: (user: User | null) => {
          set({
            user,
            isAuthenticated: !!user,
          });
        },

        updateConfig: (newConfig: Partial<AppConfig>) => {
          set(state => ({
            config: { ...state.config, ...newConfig },
          }));
        },

        toggleSidebar: () => {
          set(state => ({
            sidebarOpen: !state.sidebarOpen,
          }));
        },

        setTheme: (theme: 'light' | 'dark' | 'system') => {
          set({ theme });
        },

        // Connection monitoring
        checkConnections: async () => {
          set(state => ({
            connectionStatus: {
              ...state.connectionStatus,
              api: 'connecting',
            },
          }));

          try {
            // Test API connection
            const healthResponse = await webhookApi.getHealthStatus();

            set(state => ({
              connectionStatus: {
                api: 'connected',
                webhooks: healthResponse.status === 'healthy' ? 'connected' : 'error',
                zoho: healthResponse.services.zoho.status === 'connected' ? 'connected' : 'disconnected',
                canvas: healthResponse.services.canvas.status === 'connected' ? 'connected' : 'disconnected',
              },
            }));
          } catch (error) {
            set(state => ({
              connectionStatus: {
                ...state.connectionStatus,
                api: 'error',
              },
            }));
          }
        },

        startLiveUpdates: () => {
          const { eventStream, config } = get();

          if (eventStream || !config.features.realTimeUpdates) return;

          try {
            const stream = webhookApi.createEventStream(['feedback_received', 'priority_updated']);

            stream.onmessage = (event) => {
              const data: WebSocketEvent = JSON.parse(event.data);

              set(state => ({
                recentEvents: [data, ...state.recentEvents.slice(0, 49)], // Keep last 50 events
                lastWebhookActivity: data.timestamp,
              }));

              // Add notification for important events
              if (data.type === 'feedback_received') {
                get().addNotification({
                  type: 'info',
                  message: `New feedback received for ${data.payload.courseName}`,
                });
              }
            };

            stream.onerror = () => {
              set(state => ({
                connectionStatus: {
                  ...state.connectionStatus,
                  webhooks: 'error',
                },
              }));
            };

            set({
              eventStream: stream,
              liveUpdates: true,
            });
          } catch (error) {
            console.error('Failed to start live updates:', error);
          }
        },

        stopLiveUpdates: () => {
          const { eventStream } = get();

          if (eventStream) {
            eventStream.close();
          }

          set({
            eventStream: null,
            liveUpdates: false,
          });
        },

        // Notifications
        addNotification: (notification) => {
          const id = Date.now().toString();
          const timestamp = new Date().toISOString();

          set(state => ({
            notifications: [
              { ...notification, id, timestamp, read: false },
              ...state.notifications,
            ].slice(0, 50), // Keep last 50 notifications
          }));
        },

        markNotificationRead: (id: string) => {
          set(state => ({
            notifications: state.notifications.map(n =>
              n.id === id ? { ...n, read: true } : n
            ),
          }));
        },

        clearNotifications: () => {
          set({ notifications: [] });
        },

        // Data source actions
        testConnection: async (service: 'zoho' | 'canvas') => {
          try {
            const result = await ingestApi.testConnection(service);
            return result.connected;
          } catch (error) {
            get().handleError(error as Error, `Testing ${service} connection`);
            return false;
          }
        },

        triggerManualIngest: async (source: 'zoho' | 'canvas', params = {}) => {
          try {
            const jobId = Date.now().toString();

            // Add job to tracking
            set(state => ({
              ingestJobs: [
                {
                  id: jobId,
                  source,
                  status: 'pending',
                  startedAt: new Date().toISOString(),
                  progress: 0,
                },
                ...state.ingestJobs,
              ],
            }));

            const result = source === 'zoho'
              ? await ingestApi.ingestZohoData(params)
              : await ingestApi.ingestCanvasData(params);

            // Update job status
            set(state => ({
              ingestJobs: state.ingestJobs.map(job =>
                job.id === jobId
                  ? {
                      ...job,
                      status: result.status === 'success' ? 'completed' : 'running',
                      progress: result.status === 'success' ? 100 : 50,
                    }
                  : job
              ),
            }));

            get().addNotification({
              type: result.status === 'success' ? 'success' : 'info',
              message: `${source.toUpperCase()} ingestion ${result.status}. Processed ${result.recordsProcessed} records.`,
            });
          } catch (error) {
            get().handleError(error as Error, `Manual ${source} ingestion`);
          }
        },

        // Error handling
        handleError: (error: Error, context = 'Unknown') => {
          console.error(`Error in ${context}:`, error);

          get().addNotification({
            type: 'error',
            message: `${context}: ${error.message}`,
          });
        },
      }),
      {
        name: 'app-store',
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          theme: state.theme,
          config: state.config,
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
);