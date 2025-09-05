# Dev-Kit Overview

A lightweight toolkit for consistent development workflows. Copy into any project for instant professional structure.

## Quick Start

```bash
# 1. Copy templates to your project
cp -r templates/* /path/to/your-project/

# 2. Use the templates
cp templates/README-PROJECT.md README.md
cp templates/pr-template.md .github/pull_request_template.md

# 3. Track your work
cp templates/daily-update.md today.md
```

## What's Included

### templates/
**Ready-to-use project files:**
- `README-PROJECT.md` - Professional project documentation
- `epic-template.md` - Feature planning template
- `pr-template.md` - Pull request standards
- `daily-update.md` - Daily progress tracking

### scripts/
**Automation tools** for common tasks (shell scripts)

### reference/
**Quick lookup guides:**
- `learning-resources.md` - Curated learning materials

## Daily Workflow

```bash
# Morning: Plan your day
cp templates/daily-update.md today.md
vim today.md

# Code with conventional commits
git commit -m "feat: add user authentication"
git commit -m "fix: resolve database connection issue"

# Create PRs with template
cp templates/pr-template.md pr-description.md
```

## How to Use

1. **Starting a Project**: Copy templates you need
2. **Daily Work**: Use daily-update.md for tracking
3. **Feature Planning**: Use epic-template.md
4. **Pull Requests**: Follow pr-template.md
5. **Documentation**: Start with README-PROJECT.md

No complex setup. Just markdown templates and simple scripts.