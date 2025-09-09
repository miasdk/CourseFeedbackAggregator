import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { CheckCircle, XCircle, RefreshCw, Database } from "lucide-react";
import { DataSourceStatus as DataSourceStatusType } from "../types";

interface DataSourceStatusProps {
  status: DataSourceStatusType;
  onSync: (source: 'canvas' | 'zoho') => void;
  isSyncing: { canvas: boolean; zoho: boolean };
}

export function DataSourceStatus({ status, onSync, isSyncing }: DataSourceStatusProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const DataSourceCard = ({ 
    name, 
    source, 
    connected, 
    lastSync, 
    primaryMetric, 
    secondaryMetric,
    primaryLabel,
    secondaryLabel 
  }: {
    name: string;
    source: 'canvas' | 'zoho';
    connected: boolean;
    lastSync: string;
    primaryMetric: number;
    secondaryMetric: number;
    primaryLabel: string;
    secondaryLabel: string;
  }) => (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4" />
          <span className="font-medium">{name}</span>
        </div>
        <Badge variant={connected ? "default" : "destructive"} className="gap-1">
          {connected ? <CheckCircle className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
          {connected ? "Connected" : "Disconnected"}
        </Badge>
      </div>
      
      {connected && (
        <>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">{primaryLabel}</p>
              <p className="font-medium">{primaryMetric}</p>
            </div>
            <div>
              <p className="text-muted-foreground">{secondaryLabel}</p>
              <p className="font-medium">{secondaryMetric}</p>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted-foreground">
              Last sync: {formatDate(lastSync)}
            </p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onSync(source)}
              disabled={isSyncing[source]}
            >
              <RefreshCw className={`h-3 w-3 mr-1 ${isSyncing[source] ? 'animate-spin' : ''}`} />
              {isSyncing[source] ? 'Syncing...' : 'Sync'}
            </Button>
          </div>
        </>
      )}
    </div>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Data Sources</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <DataSourceCard
          name="Canvas LMS"
          source="canvas"
          connected={status.canvas.connected}
          lastSync={status.canvas.last_sync}
          primaryMetric={status.canvas.courses_synced}
          secondaryMetric={status.canvas.feedback_items}
          primaryLabel="Courses"
          secondaryLabel="Feedback Items"
        />
        
        <DataSourceCard
          name="Zoho CRM"
          source="zoho"
          connected={status.zoho.connected}
          lastSync={status.zoho.last_sync}
          primaryMetric={status.zoho.surveys_synced}
          secondaryMetric={status.zoho.responses}
          primaryLabel="Surveys"
          secondaryLabel="Responses"
        />
      </CardContent>
    </Card>
  );
}