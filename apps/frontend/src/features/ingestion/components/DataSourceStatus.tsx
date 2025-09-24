import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { DataSourceStatus } from "../types";

interface DataSourceStatusProps {
  status: DataSourceStatus;
  onSync: (source: 'canvas' | 'zoho') => void;
  isSyncing: { canvas: boolean; zoho: boolean };
}

export function DataSourceStatusComponent({ status, onSync, isSyncing }: DataSourceStatusProps) {
  const formatLastSync = (dateString: string) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const hours = Math.floor(diffInMinutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getStatusIndicator = (connected: boolean) => {
    return connected ? (
      <span className="w-2 h-2 bg-green-500 rounded-full inline-block" />
    ) : (
      <span className="w-2 h-2 bg-red-500 rounded-full inline-block" />
    );
  };

  const getStatusBadge = (connected: boolean) => {
    return (
      <Badge variant={connected ? "default" : "destructive"} className="text-xs">
        {connected ? "Connected" : "Disconnected"}
      </Badge>
    );
  };

  const totalFeedback = status.canvas.feedback_items + status.zoho.responses;
  const connectedSources = (status.canvas.connected ? 1 : 0) + (status.zoho.connected ? 1 : 0);

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Data Sources</CardTitle>
          <Badge variant="outline" className="text-xs">
            {connectedSources}/2 Connected
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-muted-foreground">{totalFeedback}</div>
            <div className="text-xs text-muted-foreground">Total Feedback</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-muted-foreground">{status.canvas.courses_synced}</div>
            <div className="text-xs text-muted-foreground">Courses</div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onSync('canvas')}
            disabled={isSyncing.canvas}
            className="flex-1"
          >
            {isSyncing.canvas ? "Syncing..." : "Sync Canvas"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onSync('zoho')}
            disabled={isSyncing.zoho}
            className="flex-1"
          >
            {isSyncing.zoho ? "Syncing..." : "Sync Zoho"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}