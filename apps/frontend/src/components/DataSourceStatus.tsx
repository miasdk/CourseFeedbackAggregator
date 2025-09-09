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

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg">
          Data Sources
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Canvas LMS Status */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getStatusIndicator(status.canvas.connected)}
              <span className="font-medium">Canvas LMS</span>
              {getStatusBadge(status.canvas.connected)}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onSync('canvas')}
              disabled={isSyncing.canvas}
            >
              {isSyncing.canvas ? "Syncing..." : "Sync"}
            </Button>
          </div>
          
          <div className="text-sm text-muted-foreground space-y-1">
            <div className="flex justify-between">
              <span>Last sync:</span>
              <span>
                {formatLastSync(status.canvas.last_sync)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Courses:</span>
              <span>{status.canvas.courses_synced}</span>
            </div>
            <div className="flex justify-between">
              <span>Feedback items:</span>
              <span>{status.canvas.feedback_items}</span>
            </div>
          </div>
        </div>

        <div className="border-t pt-4">
          {/* Zoho CRM Status */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIndicator(status.zoho.connected)}
                <span className="font-medium">Zoho CRM</span>
                {getStatusBadge(status.zoho.connected)}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onSync('zoho')}
                disabled={isSyncing.zoho}
              >
                {isSyncing.zoho ? "Syncing..." : "Sync"}
              </Button>
            </div>
            
            <div className="text-sm text-muted-foreground space-y-1">
              <div className="flex justify-between">
                <span>Last sync:</span>
                <span>
                  {formatLastSync(status.zoho.last_sync)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Surveys:</span>
                <span>{status.zoho.surveys_synced}</span>
              </div>
              <div className="flex justify-between">
                <span>Responses:</span>
                <span>{status.zoho.responses}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t text-xs text-muted-foreground">
          <p>Data is automatically synced every 15 minutes. Manual sync available above.</p>
        </div>
      </CardContent>
    </Card>
  );
}