# 🚀 GitHub Actions Pipelines Guide

**CallSync has 6 automated pipelines that run on GitHub.**

All pipelines are visible at: https://github.com/nighthawk369/callsync/actions

---

## 📊 All Available Pipelines

| Pipeline | Trigger | Runs On | Time | Purpose |
|----------|---------|---------|------|---------|
| **Tests** | PR / Push | PRs + main/develop | 5-10 min | Unit & integration tests |
| **Security Checks** | PR / Push | PRs + main/develop | 3-5 min | Security scanning, secrets |
| **Build** | Push to main | main only | 10 min | Docker build & push to ECR |
| **Deploy** | Merge to main | main only | 15 min | Deploy to AWS (auto) |
| **Docker** | Manual or PR | Any branch | 5 min | Build Docker image |
| **Manual Checks** | Manual trigger | Any branch | 5-10 min | Run custom checks |

---

## 🔄 Automatic Pipelines (No Setup Needed)

These run **automatically** when you:

### **1. Create a Pull Request**
```
You create PR (feature → develop or develop → main)
  ↓
GitHub Actions: Tests job starts
  ├── Backend tests (pytest)
  ├── Frontend tests (npm test)
  ├── Mobile type check (tsc)
  ├── Security checks (Bandit, Safety, TruffleHog)
  └── All must pass ✅
  ↓
You review PR
  ↓
Click "Merge" (deploys if merging to main)
```

### **2. Push to main Branch**
```
You merge PR to main
  ↓
GitHub Actions: Deploy job starts
  ├── Build Docker image
  ├── Push to ECR
  ├── Update ECS service
  ├── Run smoke tests
  └── Verify health check ✅
  ↓
Live in production!
```

### **3. Push to develop Branch**
```
You merge PR to develop
  ↓
GitHub Actions: Tests job runs
  ├── Run all tests
  ├── Verify no regressions
  └── No deployment (staging only)
  ↓
develop is updated and tested
```

---

## 🎮 Manual Pipelines (You Control)

### **Method 1: GitHub UI (Easiest)**

#### **Step 1: Go to Actions**
```
https://github.com/nighthawk369/callsync/actions
```

#### **Step 2: Select Workflow**
```
Left sidebar:
├── All workflows
├── Tests
├── Manual Checks ⭐ (NEW!)
├── Build
├── Deploy
├── Security Checks
└── Docker
```

#### **Step 3: Click "Run workflow"**
```
Click "Run workflow" button
  ↓
Select options (if available)
  ├── Which branch? (default: develop)
  ├── Which tests? (default: all)
  └── Any parameters?
  ↓
Click "Run workflow"
```

#### **Step 4: Watch It Run**
```
Pipeline starts immediately
  ↓
You see real-time logs
  ├── Step 1: ✅ Complete
  ├── Step 2: 🔄 Running...
  ├── Step 3: ⏳ Queued
  └── ...
  ↓
Final result: ✅ Success or ❌ Failed
```

---

### **Method 2: GitHub CLI (Advanced)**

#### **Run Tests Manually**
```bash
# Run all tests
gh workflow run tests.yml

# Run with specific branch
gh workflow run tests.yml --ref develop

# Run specific test scope
gh workflow run tests.yml \
  --ref develop \
  -f test_scope=backend-only
```

#### **Run Security Checks**
```bash
gh workflow run security.yml --ref develop
```

#### **Run Manual Checks (New!)**
```bash
# Run full check
gh workflow run manual-check.yml \
  -f check_type=full

# Run security only
gh workflow run manual-check.yml \
  -f check_type=security-only

# Run backend tests only
gh workflow run manual-check.yml \
  -f check_type=backend-only
```

#### **List Workflow Runs**
```bash
gh run list
gh run view <run-id>
gh run watch <run-id>
```

---

## 📋 Pipeline Details

### **1️⃣ Tests Pipeline**
**What it does:**
```
✅ Backend tests (pytest)
   - Unit tests
   - Integration tests
   - Database tests
   - 50+ test cases

✅ Frontend tests (npm)
   - Build verification
   - TypeScript check
   - Component tests

✅ Mobile tests (tsc)
   - TypeScript compilation
   - Type checking
   - React Native validation
```

**When it runs:**
- Every PR to main or develop
- Every push to main or develop
- Manual trigger (optional)

**View results:**
```
GitHub Actions → Tests → Click any run
  ↓
See logs:
├── Backend tests output
├── Frontend build output
└── Mobile type check output
```

---

### **2️⃣ Security Checks Pipeline**
**What it does:**
```
✅ Backend Security
   - Bandit (security issues)
   - Safety (vulnerable dependencies)

✅ Frontend Security
   - npm audit (dependencies)
   - Critical vulnerability detection

✅ Secret Scanning
   - TruffleHog (detects secrets)
   - Git history scanning
   - Filesystem scanning
```

**When it runs:**
- Every PR to main or develop
- Daily at midnight UTC
- Manual trigger (optional)

**View results:**
```
GitHub Actions → Security Checks → Click run
  ↓
See detailed report:
├── Bandit findings (if any)
├── npm audit report
└── Secret scanning report
```

---

### **3️⃣ Build Pipeline**
**What it does:**
```
✅ Docker build
   - Create Docker image
   - Run security scan
   
✅ Push to ECR
   - Upload to AWS ECR
   - Tag with commit hash
   
✅ Verify deployment ready
   - Image size check
   - Layer analysis
```

**When it runs:**
- Every merge to main (after tests pass)
- Manual trigger (optional)

**View results:**
```
GitHub Actions → Build → Click run
  ↓
See build details:
├── Docker build output
├── Image size: XXX MB
├── Layers: X layers
└── ECR push status: ✅
```

---

### **4️⃣ Deploy Pipeline** ⭐ Most Important
**What it does:**
```
✅ Build Docker image
✅ Push to ECR
✅ Update ECS service
   - Rolling deployment
   - Zero downtime
   - Health checks
✅ Run smoke tests
✅ Verify API health
```

**When it runs:**
- **Automatically** when code merges to main
- Never on develop (only staging)
- Manual trigger (optional via workflow_dispatch)

**View results:**
```
GitHub Actions → Deploy → Click run
  ↓
See deployment:
├── Docker build: ✅
├── ECR push: ✅
├── ECS update: ✅ (rolling)
├── Smoke tests: ✅
└── Final status: LIVE in production! 🎉
```

---

### **5️⃣ Docker Pipeline**
**What it does:**
```
✅ Build Docker image
✅ Run image security scan
✅ Verify image works
✅ Create artifact
```

**When it runs:**
- On demand (manual trigger)
- PR workflows (optional)

**View results:**
```
GitHub Actions → Docker → Click run
  ↓
See Docker build:
├── Base image: python:3.11-slim
├── Build time: X minutes
├── Final image size: XXX MB
└── Scan results: 0 vulnerabilities
```

---

### **6️⃣ Manual Checks Pipeline** 🆕
**What it does:**
```
Full Check:
  ├── Backend tests
  ├── Frontend tests
  ├── Mobile tests
  ├── Security checks
  └── Lint checks

Security Only:
  ├── Backend security
  ├── Frontend audit
  └── Secret scanning

Backend Only:
  └── pytest + linting

Frontend Only:
  └── npm tests + linting

Mobile Only:
  └── TypeScript check + build

Lint Only:
  ├── Python (black, ruff, isort)
  └── JavaScript (eslint)
```

**When it runs:**
- Manual trigger only (you control it)
- Any branch
- No automatic triggers

**How to use:**
```
1. Go to: https://github.com/nighthawk369/callsync/actions
2. Click "Manual Checks" in sidebar
3. Click "Run workflow" button
4. Select check type from dropdown:
   - full (everything)
   - security-only (quick security check)
   - tests-only (all tests)
   - backend-only (backend only)
   - frontend-only (frontend only)
   - mobile-only (mobile only)
   - lint-only (code quality)
5. Click "Run workflow"
6. Watch real-time logs ✅
```

---

## 📱 How to Access Pipelines

### **On GitHub.com**

#### **View All Pipeline Runs**
```
1. Go to https://github.com/nighthawk369/callsync
2. Click "Actions" tab (top)
3. See all workflow runs with status
```

#### **View Specific Workflow**
```
1. Actions → Click workflow name (e.g., "Tests")
2. See all runs for that workflow
3. Click any run to see details
```

#### **View Run Details**
```
1. Actions → Select workflow → Click run
2. See:
   ├── Status (✅ pass / ❌ fail)
   ├── Duration (how long)
   ├── Commits (which code)
   └── Jobs (what ran)
3. Click any job to see logs
```

#### **View Job Logs**
```
1. In run details, click job name
2. See complete output:
   ├── Each step
   ├── Commands run
   ├── Output/errors
   └── Final status
```

---

## 🎯 Common Scenarios

### **Scenario 1: You Want to Test Before Creating PR**

```bash
# Option A: Run manually on GitHub UI
1. Actions → Manual Checks → Run workflow
2. Select: full or backend-only
3. Watch logs
4. If ✅ pass: safe to create PR

# Option B: Run locally first
pytest backend/tests/
npm run build
npx tsc --noEmit
```

### **Scenario 2: You Have a Failed Pipeline**

```
PR shows: ❌ Tests failed
  ↓
Click "Details" next to failed check
  ↓
See which test failed
  ↓
Fix the code
  ↓
Push again
  ↓
Pipeline re-runs automatically ✅
```

### **Scenario 3: You Want to Deploy Manually**

```bash
# If you need to deploy without PR:
gh workflow run deploy.yml \
  --ref main \
  -f environment=production

# Or via GitHub UI:
1. Actions → Deploy
2. Click "Run workflow"
3. Select environment: dev or staging
4. Click "Run workflow"
5. Deploys start immediately
```

### **Scenario 4: You Want to Check Code Quality**

```bash
# Run linting before PR:
gh workflow run manual-check.yml \
  -f check_type=lint-only

# Or via GitHub UI:
1. Actions → Manual Checks → Run workflow
2. Select: lint-only
3. View code quality issues
4. Fix them
5. Re-run to verify
```

---

## ✅ Monitoring Your Pipelines

### **GitHub Status Checks on PR**

When you create a PR, you'll see:
```
GitHub
 ├── ✅ Tests pass
 ├── ✅ Security checks pass
 ├── ✅ Build succeeds
 └── ✅ Code review approved
 
Ready to merge!
```

Or if something fails:
```
GitHub
 ├── ❌ Tests failed
 ├── ✅ Security checks pass
 ├── ✅ Build succeeds
 └── ❌ Code review approved (waiting)

Fix tests first, then request review
```

### **Email Notifications**

You'll get emails when:
- ✉️ Pipeline fails (so you can fix it)
- ✉️ Deployment succeeds (so you know it's live)
- ✉️ Security issues found (so you can patch)

---

## 🔧 Customizing Pipelines

### **Change Test Scope**

In workflow, currently:
```yaml
on:
  workflow_dispatch:
    inputs:
      test_scope:
        options:
          - all
          - backend-only
          - frontend-only
          - mobile-only
```

You can add more options like:
```yaml
          - integration-only
          - unit-only
          - slow-tests
```

### **Add New Pipeline**

Create new file: `.github/workflows/my-pipeline.yml`
```yaml
name: My Pipeline

on:
  workflow_dispatch:  # Manual trigger

jobs:
  my-job:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: My Step
      run: echo "Hello!"
```

Then run from: Actions → My Pipeline → Run workflow

---

## 📊 Pipeline Dashboard

View all pipelines at once:
```
https://github.com/nighthawk369/callsync/actions

Shows:
├── All workflows with last status
├── Last run for each workflow
├── Success/failure rate
└── Average duration
```

---

## 🚀 Summary

**Your pipelines:**

| When | Pipeline | Auto? |
|------|----------|-------|
| Create PR | Tests + Security | ✅ Auto |
| Merge to develop | Tests | ✅ Auto |
| Merge to main | Tests + Build + Deploy | ✅ Auto |
| Anytime | Manual Checks | 🎮 You control |

**To run manually:**
```
1. GitHub UI: Actions → Select workflow → Run workflow
2. GitHub CLI: gh workflow run workflow-name.yml
```

**To check results:**
```
1. GitHub Actions tab
2. Click workflow name
3. Click run
4. View detailed logs
```

Ready to use your pipelines! 🎉
