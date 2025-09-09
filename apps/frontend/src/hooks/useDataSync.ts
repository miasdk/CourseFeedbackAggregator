import { useState, useCallback, useEffect } from 'react';
import { DataSourceStatus } from '../types';
import { apiClient } from '../services/api';
import { toast } from 'sonner';

export function useDataSync() {
  const [dataSourceStatus, setDataSourceStatus] = useState<DataSourceStatus>({
    canvas: {
      connected: false,
      last_sync: '',
      courses_synced: 0,
      feedback_items: 0
    },
    zoho: {
      connected: false,
      last_sync: '',
      surveys_synced: 0,
      responses: 0
    }
  });
  
  const [isSyncing, setIsSyncing] = useState({ canvas: false, zoho: false });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load data source status on mount
  useEffect(() => {
    loadDataSourceStatus();
  }, []);

  const loadDataSourceStatus = useCallback(async () => {
    try {
      const status = await apiClient.getDataSourceStatus();
      setDataSourceStatus(status);
    } catch (error) {
      console.error('Failed to load data source status:', error);
    }
  }, []);

  const syncDataSource = useCallback(async (source: 'canvas' | 'zoho') => {
    if (isSyncing[source]) return;

    setIsSyncing(prev => ({ ...prev, [source]: true }));
    
    try {
      const result = source === 'canvas' 
        ? await apiClient.syncCanvas()
        : await apiClient.syncZoho();
      
      const sourceName = source === 'canvas' ? 'Canvas LMS' : 'Zoho CRM';
      toast.success(`${sourceName} sync completed. ${result.synced_items} items processed.`);
      
      // Refresh status after sync
      await loadDataSourceStatus();
    } catch (error) {
      const sourceName = source === 'canvas' ? 'Canvas LMS' : 'Zoho CRM';
      toast.error(`Failed to sync ${sourceName} data. Please try again.`);
      console.error(`${source} sync error:`, error);
    } finally {
      setIsSyncing(prev => ({ ...prev, [source]: false }));
    }
  }, [isSyncing, loadDataSourceStatus]);

  const refreshDashboard = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    
    try {
      await loadDataSourceStatus();
      toast.success('Dashboard data refreshed');
    } catch (error) {
      toast.error('Failed to refresh dashboard. Please try again.');
      console.error('Dashboard refresh error:', error);
    } finally {
      setIsRefreshing(false);
    }
  }, [isRefreshing, loadDataSourceStatus]);

  return {
    dataSourceStatus,
    isSyncing,
    isRefreshing,
    syncDataSource,
    refreshDashboard,
    refresh: loadDataSourceStatus
  };
}