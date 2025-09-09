import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { AlertTriangle, CheckCircle, Clock, TrendingUp, Users } from "lucide-react";

interface StatsOverviewProps {
  totalRecommendations: number;
  showStoppers: number;
  pending: number;
  validated: number;
  averageScore: number;
}

export function StatsOverview({ 
  totalRecommendations, 
  showStoppers, 
  pending, 
  validated, 
  averageScore 
}: StatsOverviewProps) {
  
  const validationRate = totalRecommendations > 0 
    ? Math.round((validated / totalRecommendations) * 100) 
    : 0;

  const stats = [
    {
      label: "Total Issues",
      value: totalRecommendations,
      icon: <Users className="h-4 w-4" />,
      color: "text-blue-600",
      bg: "bg-blue-50"
    },
    {
      label: "Critical Issues",
      value: showStoppers,
      icon: <AlertTriangle className="h-4 w-4" />,
      color: "text-red-600",
      bg: "bg-red-50"
    },
    {
      label: "Pending Review",
      value: pending,
      icon: <Clock className="h-4 w-4" />,
      color: "text-yellow-600",
      bg: "bg-yellow-50"
    },
    {
      label: "Validated",
      value: validated,
      icon: <CheckCircle className="h-4 w-4" />,
      color: "text-green-600",
      bg: "bg-green-50"
    },
    {
      label: "Avg Priority Score",
      value: `${averageScore}/5`,
      icon: <TrendingUp className="h-4 w-4" />,
      color: "text-purple-600",
      bg: "bg-purple-50"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      {stats.map((stat, index) => (
        <Card key={index} className="relative overflow-hidden">
          <CardContent className="p-4">
            <div className={`absolute inset-0 ${stat.bg} opacity-50`} />
            <div className="relative">
              <div className="flex items-center justify-between mb-2">
                <div className={`${stat.color} ${stat.bg} p-2 rounded-lg`}>
                  {stat.icon}
                </div>
                {index === 1 && showStoppers > 0 && (
                  <Badge variant="destructive" className="text-xs">
                    URGENT
                  </Badge>
                )}
                {index === 4 && averageScore >= 4 && (
                  <Badge variant="default" className="text-xs">
                    HIGH
                  </Badge>
                )}
              </div>
              <div className="space-y-1">
                <p className={`text-2xl font-bold ${stat.color}`}>
                  {stat.value}
                </p>
                <p className="text-sm text-muted-foreground">
                  {stat.label}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      
      {/* Validation Rate Progress */}
      <Card className="md:col-span-3 lg:col-span-5">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Validation Progress</span>
            <span className="text-sm text-muted-foreground">{validationRate}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${validationRate}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            {validated} of {totalRecommendations} recommendations validated
          </p>
        </CardContent>
      </Card>
    </div>
  );
}