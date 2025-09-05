# Git Quick Reference

## Essential Commands

### Daily Workflow
```bash
# Start working
git pull                         # Get latest changes
git checkout -b feature/thing    # Create feature branch

# While coding
git add .                        # Stage changes
git commit -m "feat: add thing"  # Commit with conventional format
git push -u origin feature/thing # Push new branch

# When done
git checkout main               # Switch to main
git merge feature/thing         # Merge your changes
git branch -d feature/thing     # Delete feature branch
```

### Essential Commands
```bash
# Status & Info
git status                      # See what's changed
git log --oneline              # Commit history
git diff                       # See unstaged changes

# Undo Things
git checkout -- filename      # Discard file changes
git reset HEAD filename       # Unstage file
git reset --soft HEAD~1       # Undo last commit (keep changes)
git reset --hard HEAD~1       # Undo last commit (lose changes)

# Remote
git remote -v                  # See remotes
git push origin main           # Push to main branch
git pull                       # Pull latest changes
```

## Conventional Commits

### Format
```
<type>: <description>

feat     # New feature
fix      # Bug fix  
docs     # Documentation
style    # Formatting changes
refactor # Code refactoring
test     # Adding tests
chore    # Build tasks, dependencies
```

### Examples
```bash
git commit -m "feat: add user authentication"
git commit -m "fix: resolve login form validation"
git commit -m "docs: update API documentation"
git commit -m "refactor: extract payment service"
git commit -m "test: add unit tests for auth"
git commit -m "chore: update dependencies"
```

### Description Rules
- Use imperative mood ("add" not "added")
- No capital first letter
- No period at end
- Max 50 characters

## Troubleshooting

### Merge Conflicts
```bash
# When you see merge conflict
git status                     # See conflicted files
# Edit files to resolve conflicts
git add .                      # Mark as resolved
git commit                     # Complete the merge
```

### Accidental Commits
```bash
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo last commit and lose changes
git reset --hard HEAD~1

# Change last commit message
git commit --amend -m "new message"
```

### Branch Issues
```bash
# See all branches
git branch -a

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name

# Rename current branch
git branch -m new-branch-name
```

## .gitignore Essentials
```
# Dependencies
node_modules/
__pycache__/
.env
.env.local

# OS Files
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/

# Logs
*.log
```

Keep it simple: commit often, pull before you push, use clear commit messages.