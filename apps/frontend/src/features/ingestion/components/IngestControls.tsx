/**
 * Manual data ingestion controls
 * Allows users to trigger batch imports from Zoho and Canvas
 */

import React, { useState } from 'react';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Calendar, Database, Download, RefreshCw, AlertTriangle } from 'lucide-react';
import { useAppStore } from '../../../store';
import type { IngestRequest } from '../../../services/api/ingest';

interface IngestControlsProps {
  onIngestComplete?: (source: 'zoho' | 'canvas', result: any) => void;
}

export function IngestControls({ onIngestComplete }: IngestControlsProps) {
  const [isIngesting, setIsIngesting] = useState<Record<string, boolean>>({});
  const [lastIngest, setLastIngest] = useState<Record<string, string>>({});

  const { triggerManualIngest, testConnection, addNotification } = useAppStore();

  const handleIngest = async (source: 'zoho' | 'canvas', params?: Partial<IngestRequest>) => {
    const key = `${source}_${Date.now()}`;
    setIsIngesting(prev => ({ ...prev, [key]: true }));

    try {
      await triggerManualIngest(source, {
        testMode: false,
        limit: 100,
        ...params,
      });

      setLastIngest(prev => ({
        ...prev,
        [source]: new Date().toLocaleString(),
      }));

      addNotification({
        type: 'success',
        message: `${source.toUpperCase()} ingestion completed successfully`,
      });

      onIngestComplete?.(source, { success: true });
    } catch (error) {
      addNotification({
        type: 'error',
        message: `${source.toUpperCase()} ingestion failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsIngesting(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleTestIngest = async (source: 'zoho' | 'canvas') => {
    const key = `${source}_test`;
    setIsIngesting(prev => ({ ...prev, [key]: true }));

    try {
      await triggerManualIngest(source, {
        testMode: true,
        limit: 5,
      });

      addNotification({
        type: 'info',
        message: `${source.toUpperCase()} test completed - check preview results`,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        message: `${source.toUpperCase()} test failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    } finally {
      setIsIngesting(prev => ({ ...prev, [key]: false }));
    }
  };

  const handleConnectionTest = async (source: 'zoho' | 'canvas') => {
    const key = `${source}_connection`;
    setIsIngesting(prev => ({ ...prev, [key]: true }));

    try {
      const isConnected = await testConnection(source);

      addNotification({
        type: isConnected ? 'success' : 'warning',
        message: `${source.toUpperCase()} connection ${isConnected ? 'successful' : 'failed'}`,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        message: `${source.toUpperCase()} connection test failed`,
      });
    } finally {
      setIsIngesting(prev => ({ ...prev, [key]: false }));
    }
  };

  const isAnyOperationRunning = Object.values(isIngesting).some(Boolean);

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Zoho Ingestion */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-blue-600" />
              Zoho Survey Data
            </CardTitle>
            <CardDescription>
              Pull historical survey responses from Zoho CRM/Survey platform
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {lastIngest.zoho && (
              <div className="text-sm text-muted-foreground flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Last ingested: {lastIngest.zoho}
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleConnectionTest('zoho')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1"
              >
                <RefreshCw className={`h-4 w-4 ${isIngesting.zoho_connection ? 'animate-spin' : ''}`} />
                Test Connection
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleTestIngest('zoho')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1"
              >
                <AlertTriangle className="h-4 w-4" />
                Test Import (5 records)
              </Button>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => handleIngest('zoho')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1 flex-1"
              >
                <Download className={`h-4 w-4 ${Object.keys(isIngesting).some(k => k.startsWith('zoho_') && isIngesting[k]) ? 'animate-bounce' : ''}`} />
                Import Survey Data
              </Button>
            </div>

            <div className="text-xs text-muted-foreground">
              Imports course feedback from "Untried" section and recent responses
            </div>
          </CardContent>
        </Card>

        {/* Canvas Ingestion */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-orange-600" />
              Canvas LMS Data
            </CardTitle>
            <CardDescription>
              Sync course information and feedback from Canvas LMS
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {lastIngest.canvas && (
              <div className="text-sm text-muted-foreground flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Last synced: {lastIngest.canvas}
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleConnectionTest('canvas')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1"
              >
                <RefreshCw className={`h-4 w-4 ${isIngesting.canvas_connection ? 'animate-spin' : ''}`} />
                Test Connection
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleTestIngest('canvas')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1"
              >
                <AlertTriangle className="h-4 w-4" />
                Test Sync (Sample)
              </Button>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={() => handleIngest('canvas')}
                disabled={isAnyOperationRunning}
                className="flex items-center gap-1 flex-1"
              >
                <Download className={`h-4 w-4 ${Object.keys(isIngesting).some(k => k.startsWith('canvas_') && isIngesting[k]) ? 'animate-bounce' : ''}`} />
                Sync Course Data
              </Button>
            </div>

            <div className="text-xs text-muted-foreground">
              Pulls course details, discussions, evaluations, and quiz feedback
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Messages */}
      {isAnyOperationRunning && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-blue-700">
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span className="font-medium">Processing data ingestion...</span>
            </div>
            <p className="text-sm text-blue-600 mt-1">
              This may take a few minutes depending on the amount of data.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}