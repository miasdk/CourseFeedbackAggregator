import { useState, useCallback } from "react";
import { DataSourceStatus } from "../types";
import { mockDataSourceStatus } from "../data/mockData";
import { toast } from "sonner@2.0.3";

export function useDataSync() {
  const [dataSourceStatus] = useState<DataSourceStatus>(mockDataSourceStatus);
  const [isSyncing, setIsSyncing] = useState({ canvas: false, zoho: false });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const syncDataSource = useCallback(async (source: 'canvas' | 'zoho') => {
    if (isSyncing[source]) return;

    setIsSyncing(prev => ({ ...prev, [source]: true }));
    
    try {
      // Simulate API sync with realistic delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const sourceName = source === 'canvas' ? 'Canvas LMS' : 'Zoho CRM';
      toast.success(`${sourceName} data synced successfully`);
    } catch (error) {
      const sourceName = source === 'canvas' ? 'Canvas LMS' : 'Zoho CRM';
      toast.error(`Failed to sync ${sourceName} data. Please try again.`);
    } finally {
      setIsSyncing(prev => ({ ...prev, [source]: false }));
    }
  }, [isSyncing]);

  const refreshDashboard = useCallback(async () => {
    if (isRefreshing) return;

    setIsRefreshing(true);
    
    try {
      // Simulate dashboard refresh
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast.success("Dashboard data refreshed");
    } catch (error) {
      toast.error("Failed to refresh dashboard. Please try again.");
    } finally {
      setIsRefreshing(false);
    }
  }, [isRefreshing]);

  return {
    dataSourceStatus,
    isSyncing,
    isRefreshing,
    syncDataSource,
    refreshDashboard
  };
}