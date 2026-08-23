# 🌿 Git Workflow - CallSync Development

**Rule: No direct pushes to `main`. All changes go through PR reviews.**

---

## 📊 Branch Strategy

```
main (production)
  ↑
  └─ PR review required (you approve)
     ↑
     └─ develop (integration)
        ↑
        └─ feature branches (your work)
```

| Branch | Purpose | Auto Deploy? | PR Required? |
|--------|---------|--------------|--------------|
| `main` | Production live | ✅ YES | ✅ YES (must approve) |
| `develop` | Integration/testing | ❌ NO | ✅ YES |
| `feature/*` | Feature work | ❌ NO | ✅ YES (to develop) |
| `bugfix/*` | Bug fixes | ❌ NO | ✅ YES (to develop) |
| `hotfix/*` | Production bugs | ❌ NO | ✅ YES (to main) |

---

## 🚀 Development Workflow

### **Scenario 1: Implementing Phase 11 (Calendar Integration)**

#### **Step 1: Create Feature Branch**
```bash
# Make sure you're on develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/phase-11-calendar

# Or:
git switch -c feature/phase-11-calendar
```

#### **Step 2: Do Your Work**
```bash
# Make changes, commit regularly
git add backend/app/calendar/
git commit -m "feat: add Google Calendar API integration"

git add backend/tests/
git commit -m "test: add calendar integration tests"

# Push to GitHub
git push origin feature/phase-11-calendar
```

#### **Step 3: Create Pull Request**
```bash
# Via GitHub UI:
# 1. Go to https://github.com/nighthawk369/callsync/pulls
# 2. Click "New pull request"
# 3. Base: develop | Compare: feature/phase-11-calendar
# 4. Add title: "Phase 11: Calendar Integration"
# 5. Add description
# 6. Click "Create pull request"

# Via CLI:
gh pr create \
  --base develop \
  --head feature/phase-11-calendar \
  --title "Phase 11: Calendar Integration" \
  --body "Implements Google and Microsoft calendar integration"
```

#### **Step 4: GitHub Actions Tests Run**
```
PR Created
  ↓
GitHub Actions: Tests job runs
  ├── Backend tests: pytest
  ├── Frontend tests: npm test
  ├── Mobile tests: tsc
  └── Terraform validation
  ↓
All tests pass ✅
PR ready for review
```

#### **Step 5: You Review & Approve PR**
```
GitHub PR page
  ↓
Click "Files changed" → review code
  ↓
Click "Review changes" → select "Approve"
  ↓
Click "Merge pull request"
  ↓
Confirm "Squash and merge" or "Create a merge commit"
  ↓
Delete branch (optional)
```

#### **Result**
```
feature/phase-11-calendar → merged to develop ✅
develop → no auto-deploy (still staging)
Wait for release → merge develop to main
```

---

### **Scenario 2: Weekly Release to Production**

#### **When Ready to Deploy to Production:**

```bash
# Make sure develop has all features tested
git checkout develop
git pull origin develop

# Create release PR to main
gh pr create \
  --base main \
  --head develop \
  --title "Release v1.1 - Phase 11 Calendar Integration" \
  --body "
## Changes
- Phase 11: Calendar Integration
- Bug fixes from Phase 10

## Testing Done
- ✅ All tests passing
- ✅ Tested locally
- ✅ Tested on staging
- ✅ No regressions

## Checklist
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Security checks pass
- ✅ Performance verified
"
```

#### **You Review Release PR**
```
Release PR to main
  ↓
Click "Approve"
  ↓
Click "Merge pull request"
  ↓
develop → main ✅
```

#### **Automatic Deployment Starts**
```
Code merged to main
  ↓
GitHub Actions: Deploy job runs
  ├── Build Docker image
  ├── Push to ECR
  ├── Update ECS service
  ├── Run smoke tests
  └── Verify API health
  ↓
Live in production! 🎉
```

---

## 🔄 Common Workflows

### **Workflow A: Add New Feature**
```bash
# 1. Create branch
git checkout -b feature/my-feature develop

# 2. Do work
# ... code ...

# 3. Commit & push
git push origin feature/my-feature

# 4. Create PR to develop
gh pr create --base develop --head feature/my-feature

# 5. You approve PR in GitHub UI
# 6. PR merged to develop

# 7. Create release PR when ready
gh pr create --base main --head develop

# 8. You approve release PR
# 9. Auto-deploys to production ✅
```

### **Workflow B: Fix Bug on Production**
```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/critical-bug main

# 2. Fix bug
# ... fix code ...

# 3. Commit & push
git push origin hotfix/critical-bug

# 4. Create PR directly to main
gh pr create --base main --head hotfix/critical-bug

# 5. You approve PR
# 6. Auto-deploys to production ✅
# 7. Also merge to develop: git merge hotfix/critical-bug develop
```

### **Workflow C: Update After Review Comments**
```bash
# While in feature branch, if you get review comments:

# 1. Make changes
# ... update code ...

# 2. Commit with meaningful message
git commit -m "refactor: address review comments on calendar API"

# 3. Push again (same branch)
git push origin feature/phase-11-calendar

# 4. PR automatically updates with new commits
# 5. Reviewer can see the changes
# 6. Once approved, merge
```

---

## 📋 GitHub Actions Pipeline

### **On Pull Request to develop or main:**
```
Push to PR branch
  ↓
GitHub Actions: Tests
  ├── Backend tests ✅
  ├── Frontend tests ✅
  ├── Mobile tests ✅
  ├── Security checks ✅
  ├── Dependency check ✅
  └── Secret scanning ✅
  ↓
All checks pass ✅
PR reviewable ✅
```

### **On Merge to main:**
```
Merge PR to main
  ↓
GitHub Actions: Deploy
  ├── Build Docker image ✅
  ├── Push to ECR ✅
  ├── Update ECS service ✅
  ├── Zero-downtime rolling update ✅
  ├── Run smoke tests ✅
  └── Verify API health ✅
  ↓
Live in production! 🎉
```

---

## 🛡️ Branch Protection Rules

### **What These Rules Enforce:**

**For `main` branch:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass (tests, security, etc.)
- ✅ Require branches to be up to date
- ✅ Dismiss stale PR approvals when new commits pushed
- ✅ Require code owner review

**For `develop` branch:**
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

### **Result:**
```
Trying to push directly to main:
git push origin main
→ REJECTED ❌
  "Direct push not allowed. Use pull request."

Trying to merge PR without approval:
Click "Merge pull request" without approval
→ REJECTED ❌
  "At least 1 approval required"

Trying to merge PR with failing tests:
Click "Merge pull request" with ❌ tests
→ REJECTED ❌
  "Required status checks must pass"

✅ Only way to deploy:
  1. Create PR
  2. Tests pass automatically
  3. You approve PR
  4. Merge to main
  5. Auto-deploy happens ✅
```

---

## 📱 Command Cheat Sheet

### **Create Feature Branch**
```bash
git checkout -b feature/my-feature develop
```

### **Push Branch**
```bash
git push origin feature/my-feature
```

### **Create PR**
```bash
# Via CLI
gh pr create --base develop --head feature/my-feature --title "My Feature"

# Via GitHub UI
# 1. https://github.com/nighthawk369/callsync/pulls
# 2. "New pull request"
# 3. Select branches
# 4. "Create pull request"
```

### **View PRs**
```bash
gh pr list
gh pr view <number>
```

### **Approve PR**
```bash
# Via GitHub UI (easiest)
# 1. https://github.com/nighthawk369/callsync/pulls/<number>
# 2. "Review changes"
# 3. "Approve"
# 4. "Merge pull request"

# Via CLI (advanced)
gh pr review <number> --approve
gh pr merge <number> --squash
```

### **Switch Branches**
```bash
git checkout develop        # Old way
git switch develop          # New way (cleaner)

git checkout -b feature/x   # Old way
git switch -c feature/x     # New way
```

### **Update Your Branch**
```bash
# Get latest from develop
git fetch origin
git rebase origin/develop

# Or merge if you prefer
git merge origin/develop
```

### **Delete Branch**
```bash
# Local
git branch -d feature/my-feature

# Remote
git push origin --delete feature/my-feature

# Both at once
gh pr delete <number> --delete-branch
```

---

## ✅ Approval Checklist

**When reviewing your own PR, check:**

- [ ] Code follows project style
- [ ] All tests pass (green checkmarks)
- [ ] No security warnings
- [ ] No hardcoded secrets (check logs)
- [ ] Database migrations safe (if any)
- [ ] API changes documented (if any)
- [ ] No performance regressions
- [ ] Dependencies updated safely (if any)

**Then:**
```
1. Click "Review changes"
2. Select "Approve"
3. Click "Merge pull request"
4. Confirm "Create a merge commit" or "Squash and merge"
5. Delete branch
```

---

## 🚨 Rules to Never Break

| Rule | Why | Consequence |
|------|-----|-------------|
| Never push to `main` directly | Ensures review gate | Auto-deploy blocked ❌ |
| Never merge without tests passing | Prevent breaking prod | Deploy rejected ❌ |
| Never merge without approval | Review quality gate | Merge blocked ❌ |
| Never commit secrets | Security risk | Secret scanning catches it ❌ |
| Never rewrite history on main | Breaks releases | Complicated recovery |

---

## 🎯 Your Workflow Starting Tomorrow

```
9:00 AM:  git checkout -b feature/phase-11
9:01 AM:  Start coding
...
4:00 PM:  git push origin feature/phase-11
4:01 PM:  Create PR on GitHub UI
4:05 PM:  Tests finish automatically ✅
4:06 PM:  You review code, click "Approve"
4:07 PM:  You click "Merge pull request"
4:08 PM:  Code merged to develop (no deploy)

End of Week:
Friday 5 PM: Create release PR develop→main
Friday 5:05 PM: You review & approve
Friday 5:06 PM: Auto-deploy starts ✅
Friday 5:15 PM: Live in production! 🎉
```

---

## 📞 If You Need Help

```bash
# See what branch you're on
git branch

# See branches on GitHub
git branch -a

# See recent commits
git log --oneline -10

# See which commits are ahead of main
git log main..HEAD --oneline

# Check PR status
gh pr list
gh pr view <number>
```

---

**Status: Workflow Ready** ✅

You have:
- ✅ `develop` branch created
- ✅ Deploy workflow locked to `main` only
- ✅ Test workflow running on PRs
- ✅ Zero-downtime deployment on main merge
- ✅ Git workflow documented

**Start Phase 11 with:**
```bash
git checkout -b feature/phase-11-calendar develop
```

All changes go through your approval before deploying! 🚀
