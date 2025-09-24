/**
 * Real-time webhook activity monitor
 * Shows recent webhook events and system health
 */

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import {
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  AlertCircle,
  Database,
  Zap
} from 'lucide-react';
import { useAppStore } from '../../../store';
import { webhookApi } from '../../../services/api/webhooks';
import type { WebhookEvent, WebhookStats } from '../../../services/api/webhooks';

export function WebhookMonitor() {
  const [events, setEvents] = useState<WebhookEvent[]>([]);
  const [stats, setStats] = useState<WebhookStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { connectionStatus, liveUpdates } = useAppStore();

  // Fetch recent events and stats
  const fetchWebhookData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [eventsResponse, statsResponse] = await Promise.all([
        webhookApi.getRecentEvents({ limit: 10 }),
        webhookApi.getWebhookStats('24h'),
      ]);

      setEvents(eventsResponse.events);
      setStats(statsResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch webhook data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebhookData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchWebhookData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getEventStatusIcon = (event: WebhookEvent) => {
    if (event.error) {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
    if (event.processed) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    return <Clock className="h-4 w-4 text-yellow-500" />;
  };

  const getEventStatusBadge = (event: WebhookEvent) => {
    if (event.error) {
      return <Badge variant="destructive">Failed</Badge>;
    }
    if (event.processed) {
      return <Badge variant="default">Processed</Badge>;
    }
    return <Badge variant="secondary">Pending</Badge>;
  };

  const getSourceBadge = (source: string) => {
    const colors = {
      zoho_survey: 'bg-blue-100 text-blue-800',
      canvas_lms: 'bg-orange-100 text-orange-800',
    };

    return (
      <Badge
        variant="outline"
        className={colors[source as keyof typeof colors] || 'bg-gray-100 text-gray-800'}
      >
        {source.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Webhook System Status
          </CardTitle>
          <CardDescription>
            Real-time monitoring of data ingestion from external sources
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus.webhooks === 'connected' ? 'bg-green-500' :
                connectionStatus.webhooks === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm font-medium">Webhooks</span>
            </div>

            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus.zoho === 'connected' ? 'bg-green-500' :
                connectionStatus.zoho === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm font-medium">Zoho</span>
            </div>

            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus.canvas === 'connected' ? 'bg-green-500' :
                connectionStatus.canvas === 'error' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm font-medium">Canvas</span>
            </div>

            <div className="flex items-center gap-2">
              {liveUpdates ? (
                <Zap className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-yellow-500" />
              )}
              <span className="text-sm font-medium">Live Updates</span>
            </div>
          </div>

          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
              <div>
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-muted-foreground">Total Events</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">{stats.processed}</div>
                <div className="text-sm text-muted-foreground">Processed</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
                <div className="text-sm text-muted-foreground">Failed</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{Math.round(stats.avgProcessingTime)}ms</div>
                <div className="text-sm text-muted-foreground">Avg Time</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Events */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Webhook Events</CardTitle>
            <CardDescription>
              Latest incoming data from Zoho Surveys and Canvas LMS
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchWebhookData}
            disabled={loading}
            className="flex items-center gap-1"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-8 text-red-500">
              <AlertCircle className="h-5 w-5 mr-2" />
              {error}
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No webhook events received yet</p>
              <p className="text-sm">Events will appear here when data is received from external sources</p>
            </div>
          ) : (
            <div className="space-y-3">
              {events.map((event) => (
                <div
                  key={event.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                >
                  <div className="flex items-center gap-3">
                    {getEventStatusIcon(event)}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        {getSourceBadge(event.source)}
                        {event.courseName && (
                          <span className="text-sm font-medium">{event.courseName}</span>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {event.eventType} • {formatTimestamp(event.timestamp)}
                      </div>
                      {event.error && (
                        <div className="text-xs text-red-600 mt-1">{event.error}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {event.processingTime && (
                      <span className="text-xs text-muted-foreground">
                        {event.processingTime}ms
                      </span>
                    )}
                    {getEventStatusBadge(event)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}