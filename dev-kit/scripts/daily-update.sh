#!/bin/bash

# Daily Progress Update Script - Hybrid Evolution System
# Usage: ./daily-update.sh [epic-number] [time-spent] [completed-tasks]

EPIC_NUMBER=$1
TIME_SPENT=${2:-"2h"}
COMPLETED_TASKS=$3
REPO_OWNER="miasdk"  # Change to your GitHub username

if [ -z "$EPIC_NUMBER" ]; then
    echo "❌ Usage: ./daily-update.sh [epic-number] [time-spent] [completed-tasks]"
    echo "   Example: ./daily-update.sh 1 '2.5h' 'Set up Django models, configured database'"
    exit 1
fi

if [ -z "$COMPLETED_TASKS" ]; then
    echo "❌ Please specify completed tasks"
    echo "   Example: 'Set up Django models, configured database, wrote initial tests'"
    exit 1
fi

# Get project name from current directory or git remote
PROJECT_NAME=$(basename "$(git rev-parse --show-toplevel)" 2>/dev/null || basename "$PWD")
REPO="$REPO_OWNER/$PROJECT_NAME"

# Get current date and time
CURRENT_DATE=$(date +"%Y-%m-%d")
CURRENT_TIME=$(date +"%H:%M")

# Create daily progress comment
PROGRESS_COMMENT="## Daily Progress Update - $CURRENT_DATE

### ⏰ Time Investment
**Time Spent**: $TIME_SPENT  
**Session Time**: $CURRENT_TIME

### ✅ Completed Tasks
$COMPLETED_TASKS

### 🧠 Technical Decisions & Learnings
- [Add key technical decisions made today]
- [Note any important learnings or insights]
- [Document architecture choices or trade-offs]

### 📝 Code Quality
- [ ] Code documented and commented
- [ ] Tests written for new functionality
- [ ] No breaking changes introduced
- [ ] Git commits are clean and descriptive

### 🔄 Next Session Priority
- [Priority 1: Most important task for next session]
- [Priority 2: Secondary task if time permits]
- [Priority 3: Additional tasks]

### 🚧 Current Blockers
- [List any blockers or questions for next session]
- [Note any research needed or decisions pending]

---
*Updated via Hybrid Evolution System - $(date)*"

echo "📝 Posting daily update to Epic #$EPIC_NUMBER..."

# Post comment to epic issue
gh issue comment "$EPIC_NUMBER" \
    --repo "$REPO" \
    --body "$PROGRESS_COMMENT"

if [ $? -eq 0 ]; then
    echo "✅ Daily progress posted successfully!"
    echo "🔗 View epic: https://github.com/$REPO/issues/$EPIC_NUMBER"
    
    # Optional: Update epic title with progress indicator
    TOTAL_TASKS=$(gh issue view "$EPIC_NUMBER" --repo "$REPO" --json body --jq '.body' | grep -c "- \[ \]")
    COMPLETED_TASKS_COUNT=$(gh issue view "$EPIC_NUMBER" --repo "$REPO" --json body --jq '.body' | grep -c "- \[x\]")
    
    if [ "$TOTAL_TASKS" -gt 0 ]; then
        PROGRESS_PERCENT=$(echo "scale=0; $COMPLETED_TASKS_COUNT * 100 / ($TOTAL_TASKS + $COMPLETED_TASKS_COUNT)" | bc -l)
        echo "📊 Sprint Progress: $COMPLETED_TASKS_COUNT tasks completed (~$PROGRESS_PERCENT% progress)"
    fi
    
    echo ""
    echo "🎯 Quick tips for next session:"
    echo "1. Review the blockers section before starting"
    echo "2. Focus on Priority 1 task first"
    echo "3. Use the project context in SETUP.md for AI assistance"
    echo "4. Update epic checkboxes as you complete subtasks"
else
    echo "❌ Failed to post progress update. Check your GitHub CLI setup."
    exit 1
fi