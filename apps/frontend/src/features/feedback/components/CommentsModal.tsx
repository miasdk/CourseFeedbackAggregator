import React from "react";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import { MessageSquare, Star, Calendar } from "lucide-react";
import { Recommendation } from "../types";

interface CommentsModalProps {
  recommendation: Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
}

export function CommentsModal({ recommendation, isOpen, onClose }: CommentsModalProps) {
  if (!recommendation) return null;

  // Use actual evidence from the recommendation or fallback to basic info
  const evidence = recommendation.evidence || [
    {
      quote: recommendation.description,
      source: "system",
      created_at: recommendation.created_at
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSourceBadge = (source: string) => {
    switch (source) {
      case 'canvas': return <Badge variant="outline" className="text-xs bg-blue-50">Canvas LMS</Badge>;
      case 'zoho': return <Badge variant="outline" className="text-xs bg-purple-50">Zoho Survey</Badge>;
      default: return <Badge variant="outline" className="text-xs">{source}</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRatingStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" />);
    }
    
    if (hasHalfStar) {
      stars.push(<Star key="half" className="h-3 w-3 fill-yellow-400/50 text-yellow-400" />);
    }
    
    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="h-3 w-3 text-gray-300" />);
    }
    
    return stars;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              <h2 className="text-lg font-semibold">Student Feedback</h2>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl font-semibold"
            >
              ×
            </button>
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {recommendation.course_name} • {recommendation.title}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">

        <div className="space-y-4">
          {/* Feedback Items */}
          <div className="space-y-3">
            <h3 className="font-medium text-sm">Individual Comments</h3>
            {evidence.map((item, index) => (
              <Card key={index} className="border-l-4 border-l-orange-200">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getSourceBadge(item.source)}
                      {item.severity && (
                        <Badge className={getSeverityColor(item.severity)} variant="secondary">
                          {item.severity.toUpperCase()}
                        </Badge>
                      )}
                    </div>
                    {item.created_at && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {formatDate(item.created_at)}
                      </div>
                    )}
                  </div>
                  
                  <blockquote className="text-sm mb-3 italic border-l-2 border-muted pl-3">
                    "{item.quote}"
                  </blockquote>
                  
                  <div className="flex items-center justify-between">
                    {item.rating && (
                      <div className="flex items-center gap-1">
                        {getRatingStars(item.rating)}
                        <span className="text-xs text-muted-foreground ml-1">
                          ({item.rating}/5)
                        </span>
                      </div>
                    )}
                    {item.student_email && (
                      <div className="text-xs text-muted-foreground">
                        {item.student_email}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
}