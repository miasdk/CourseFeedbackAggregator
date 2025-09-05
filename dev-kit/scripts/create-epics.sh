#!/bin/bash

# Epic Creation Script - Hybrid Evolution System
# Usage: ./create-epics.sh [project-name] [sprint-count]

PROJECT_NAME=$1
SPRINT_COUNT=${2:-4}
REPO_OWNER="miasdk"  # Change to your GitHub username
REPO="$PROJECT_NAME"

echo "🚀 Creating $SPRINT_COUNT epics for $PROJECT_NAME..."

# Epic templates based on sprint count
case $SPRINT_COUNT in
  2)
    EPICS=("Foundation & Core Features" "Integration & Deploy")
    TIMELINES=("Week 1" "Week 2")
    DESCRIPTIONS=("Set up architecture, core models, and basic functionality" "Frontend integration, testing, and deployment")
    ;;
  3)
    EPICS=("Foundation" "Core Features & Integration" "Polish & Deploy")
    TIMELINES=("Week 1" "Week 2" "Week 3")
    DESCRIPTIONS=("Set up architecture and core models" "Main functionality and frontend integration" "Testing, polish, and deployment")
    ;;
  4)
    EPICS=("Foundation" "Core Features" "Integration" "Polish & Deploy")
    TIMELINES=("Week 1" "Week 2" "Week 3" "Week 4")
    DESCRIPTIONS=("Architecture setup and core models" "Main business logic and functionality" "Frontend and API integration" "Testing, deployment, and documentation")
    ;;
  6)
    EPICS=("Foundation" "Core Backend" "Advanced Features" "Frontend Integration" "Testing & Security" "Deploy & Polish")
    TIMELINES=("Week 1" "Week 2" "Week 3" "Week 4" "Week 5" "Week 6")
    DESCRIPTIONS=("Architecture and basic setup" "Core backend functionality" "Advanced business logic" "Frontend and user interface" "Comprehensive testing and security" "Deployment and final polish")
    ;;
  *)
    echo "❌ Unsupported sprint count. Use 2, 3, 4, or 6."
    exit 1
    ;;
esac

# Generate epic issues using GitHub CLI
for i in "${!EPICS[@]}"; do
  SPRINT_NUM=$((i + 1))
  EPIC_TITLE="Epic: Sprint $SPRINT_NUM - ${EPICS[$i]}"
  TIMELINE="${TIMELINES[$i]}"
  DESCRIPTION="${DESCRIPTIONS[$i]}"
  
  echo "📋 Creating: $EPIC_TITLE"
  
  # Create epic issue with template
  gh issue create \
    --repo "$REPO_OWNER/$REPO" \
    --title "$EPIC_TITLE" \
    --label "epic,sprint-$SPRINT_NUM,priority-high" \
    --body "## Epic Description
$DESCRIPTION

## Sprint Timeline
**Start Date**: TBD (Update when starting sprint)
**End Date**: TBD (Update when starting sprint)
**Duration**: $TIMELINE

## Sprint Goals
- [ ] Goal 1: [Define specific technical objective]
- [ ] Goal 2: [Define specific functionality objective]
- [ ] Goal 3: [Define specific quality objective]
- [ ] Goal 4: [Define specific documentation objective]

## Subtasks

### Setup & Architecture
- [ ] Set up development environment
- [ ] Configure project structure
- [ ] Initialize core components
- [ ] Set up version control workflows

### Development Tasks
- [ ] Task 1: [Specific implementation task]
- [ ] Task 2: [Specific implementation task]
- [ ] Task 3: [Specific implementation task]
- [ ] Task 4: [Specific implementation task]

### Quality Assurance
- [ ] Write unit tests for core functionality
- [ ] Perform integration testing
- [ ] Code review and refactoring
- [ ] Update documentation

### Sprint Deliverables
- [ ] Deliverable 1: [Specific output]
- [ ] Deliverable 2: [Specific output]
- [ ] Deliverable 3: [Specific output]
- [ ] Demo preparation and presentation

## Acceptance Criteria
- [ ] All subtasks completed successfully
- [ ] Code quality standards met
- [ ] Documentation updated and comprehensive
- [ ] Tests passing and coverage adequate
- [ ] Sprint goals achieved and validated

## Time Allocation
**Estimated Total**: 14-20 hours
**Daily Target**: 2-3 hours
**Buffer Time**: 20% for unexpected challenges

## Notes
- Update this epic daily with progress
- Use \`./scripts/daily-update.sh $SPRINT_NUM\` for automated updates
- Tag AI agent with context when requesting help

---
**Epic created by Hybrid Evolution System**"

done

echo "✅ Created $SPRINT_COUNT epic issues successfully!"
echo "🔗 View epics: https://github.com/$REPO_OWNER/$REPO/issues"
echo ""
echo "📝 Next steps:"
echo "1. Update epic start/end dates as you begin each sprint"
echo "2. Customize subtasks based on your specific project requirements"
echo "3. Use ./scripts/daily-update.sh for progress tracking"
echo "4. Run ./scripts/upgrade.sh for advanced project management features"