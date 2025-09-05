import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  AlertTriangle, 
  Clock, 
  Users, 
  ExternalLink, 
  Eye, 
  CheckCircle,
  ArrowRight,
  MessageSquare,
  Target
} from 'lucide-react';

interface Recommendation {
  id: string;
  course: string;
  module: string;
  priority: number;
  issue: string;
  impact: 'High' | 'Medium' | 'Low';
  effort: 'High' | 'Medium' | 'Low';
  studentsAffected: number;
  source: 'Canvas LMS' | 'Zoho Survey';
  sourceId: string;
  feedback: string;
  reviewer: string;
  status: 'pending' | 'in_progress' | 'completed';
  factors: {
    impact: number;
    urgency: number;
    effort: number;
    strategic: number;
    trend: number;
  };
}

interface PriorityRecommendationsProps {
  onRecommendationClick?: (rec: Recommendation) => void;
}

const PriorityRecommendations: React.FC<PriorityRecommendationsProps> = ({ onRecommendationClick }) => {
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  // Real recommendations based on actual course data
  const recommendations: Recommendation[] = [
    {
      id: '1',
      course: 'IT and Cybersecurity Leadership',
      module: 'Module 1',
      priority: 8.7,
      issue: 'Leadership Style Inconsistency',
      impact: 'High',
      effort: 'Medium',
      studentsAffected: 23,
      source: 'Canvas LMS',
      sourceId: 'GuBq7vM9',
      feedback: 'Video 1 and Video 2 both talk about attributes of a leader, but those attributes are different. This offers inconsistency.',
      reviewer: 'Michael Vetri',
      status: 'pending',
      factors: {
        impact: 9.2,
        urgency: 8.5,
        effort: 6.0,
        strategic: 9.0,
        trend: 8.8
      }
    },
    {
      id: '2',
      course: 'Customer Experience Program',
      module: 'Vision Development',
      priority: 7.3,
      issue: 'Missing Implementation Roadmap',
      impact: 'Medium',
      effort: 'Low',
      studentsAffected: 15,
      source: 'Zoho Survey',
      sourceId: 'ZS-2024-08',
      feedback: 'A vision statement is not enough - need roadmap, objectives, and proof points that vision has been achieved.',
      reviewer: 'Course Survey Respondent',
      status: 'pending',
      factors: {
        impact: 7.5,
        urgency: 6.8,
        effort: 8.5,
        strategic: 8.0,
        trend: 6.5
      }
    },
    {
      id: '3',
      course: 'Transformative Leadership 2.0',
      module: 'Democratic Leadership',
      priority: 6.1,
      issue: 'Context Limitations Not Addressed',
      impact: 'Medium',
      effort: 'Medium',
      studentsAffected: 18,
      source: 'Canvas LMS',
      sourceId: 'TL-Rev-032',
      feedback: 'Democratic leadership context missing - not applicable in high-tempo environments like incident response.',
      reviewer: 'Leadership Course Evaluation',
      status: 'in_progress',
      factors: {
        impact: 6.8,
        urgency: 5.2,
        effort: 6.0,
        strategic: 7.5,
        trend: 5.8
      }
    }
  ];

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'border-red-500 bg-red-50';
    if (priority >= 6) return 'border-yellow-500 bg-yellow-50';
    return 'border-green-500 bg-green-50';
  };

  const getPriorityLabel = (priority: number) => {
    if (priority >= 8) return { label: 'Critical', color: 'text-red-700' };
    if (priority >= 6) return { label: 'High', color: 'text-yellow-700' };
    return { label: 'Medium', color: 'text-green-700' };
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-orange-500" />;
      case 'in_progress': return <Target className="w-4 h-4 text-blue-500" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const ExplanationModal: React.FC<{ rec: Recommendation; onClose: () => void }> = ({ rec, onClose }) => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Why This Priority?</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">×</button>
        </div>
        
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">{rec.course} - {rec.module}</h4>
            <p className="text-sm text-gray-600 mb-2">{rec.issue}</p>
            <div className="text-lg font-bold text-gray-900">Priority Score: {rec.priority.toFixed(1)}/10</div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {Object.entries(rec.factors).map(([factor, score]) => (
              <div key={factor} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="capitalize text-sm font-medium text-gray-700">{factor}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${(score/10) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-bold text-gray-900">{score.toFixed(1)}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-2">Source Evidence</h4>
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">{rec.source}</span>
                <button className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1">
                  <ExternalLink className="w-3 h-3" />
                  View Source
                </button>
              </div>
              <p className="text-sm text-blue-800 italic">"{rec.feedback}"</p>
              <p className="text-xs text-blue-600 mt-2">- {rec.reviewer}</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-gray-600">
              Impact: {rec.studentsAffected} students affected
            </div>
            <button 
              onClick={onClose}
              className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors"
            >
              Mark as Reviewed
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Priority Recommendations</h2>
          <p className="text-gray-600 text-sm">Explainable course improvement priorities based on student feedback</p>
        </div>
        <div className="text-sm text-gray-500">
          {recommendations.filter(r => r.status === 'pending').length} pending review
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec, index) => {
          const priorityStyle = getPriorityColor(rec.priority);
          const priorityLabel = getPriorityLabel(rec.priority);
          
          return (
            <motion.div
              key={rec.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`bg-white border-l-4 ${priorityStyle} rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer`}
              onClick={() => onRecommendationClick?.(rec)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-xs font-bold px-2 py-1 rounded ${priorityLabel.color} bg-white`}>
                      {priorityLabel.label}
                    </span>
                    <div className="text-lg font-bold text-gray-900">
                      {rec.priority.toFixed(1)}
                    </div>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedRec(rec);
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                    >
                      <Eye className="w-4 h-4" />
                      Why?
                    </button>
                  </div>
                  
                  <h3 className="font-semibold text-gray-900 mb-1">
                    {rec.course} - {rec.module}
                  </h3>
                  
                  <p className="text-gray-700 mb-2">{rec.issue}</p>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {rec.studentsAffected} students
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      {rec.source}
                    </div>
                    <div className="flex items-center gap-2">
                      <span>Impact: {rec.impact}</span>
                      <span>•</span>
                      <span>Effort: {rec.effort}</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {getStatusIcon(rec.status)}
                  <ArrowRight className="w-4 h-4 text-gray-400" />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-6 mt-8 p-6 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {recommendations.reduce((sum, rec) => sum + rec.studentsAffected, 0)}
          </div>
          <div className="text-sm text-gray-600">Students Impacted</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {recommendations.filter(r => r.priority >= 8).length}
          </div>
          <div className="text-sm text-gray-600">Critical Issues</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {recommendations.filter(r => r.effort === 'Low').length}
          </div>
          <div className="text-sm text-gray-600">Quick Wins</div>
        </div>
      </div>

      {/* Explanation Modal */}
      {selectedRec && (
        <ExplanationModal 
          rec={selectedRec} 
          onClose={() => setSelectedRec(null)} 
        />
      )}
    </div>
  );
};

export default PriorityRecommendations;