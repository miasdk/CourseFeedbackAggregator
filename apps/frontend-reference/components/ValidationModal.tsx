/**
 * Validation Modal Component
 * 
 * Modal for instructors to write reviewer notes before marking
 * a recommendation as validated
 */

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { CheckCircle, FileText } from 'lucide-react';
import { Recommendation } from '../types';

interface ValidationModalProps {
  recommendation: Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
  onValidate: (recommendation: Recommendation, notes: string) => void;
}

export function ValidationModal({
  recommendation,
  isOpen,
  onClose,
  onValidate
}: ValidationModalProps) {
  const [reviewerNotes, setReviewerNotes] = useState('');

  const handleValidate = () => {
    if (recommendation && reviewerNotes.trim()) {
      onValidate(recommendation, reviewerNotes.trim());
      setReviewerNotes('');
      onClose();
    }
  };

  const handleClose = () => {
    setReviewerNotes('');
    onClose();
  };

  if (!recommendation) return null;

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Validate Recommendation
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Recommendation Summary */}
          <div className="bg-muted/50 rounded-lg p-4 space-y-2">
            <div className="flex items-start justify-between">
              <h3 className="font-medium">{recommendation.title}</h3>
              <Badge variant={recommendation.category === 'Critical' ? 'destructive' : 'secondary'}>
                {recommendation.category}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{recommendation.description}</p>
            <div className="flex items-center gap-4 text-sm">
              <span>Priority Score: <strong>{recommendation.priorityScore}/5</strong></span>
              <span>Course: <strong>{recommendation.courseId}</strong></span>
            </div>
          </div>

          {/* Reviewer Notes Input */}
          <div className="space-y-3">
            <Label htmlFor="reviewer-notes" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Reviewer Notes
            </Label>
            <Textarea
              id="reviewer-notes"
              placeholder="Enter your validation notes, review comments, and any action items for implementation..."
              value={reviewerNotes}
              onChange={(e) => setReviewerNotes(e.target.value)}
              className="min-h-32 resize-none"
            />
            <p className="text-xs text-muted-foreground">
              These notes will be saved with the validation and can be referenced later for implementation tracking.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleValidate}
            disabled={!reviewerNotes.trim()}
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Validate & Save Notes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}