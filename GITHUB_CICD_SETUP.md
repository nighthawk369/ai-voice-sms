# 🔄 GitHub CI/CD Setup Guide for CallSync

## Overview

Once you deploy locally with `DEPLOY_AUTOMATED.sh`, set up GitHub Actions to automatically:
1. Run tests on every PR
2. Build Docker images on merge to main
3. Deploy to AWS automatically

---

## Step 1: Get Your AWS Credentials

You already have these from `aws configure`:

```bash
# View your AWS credentials (they're stored locally)
cat ~/.aws/credentials
```

You'll see:
```
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = wJal...
```

**Save these values** - you'll need them in Step 2.

---

## Step 2: Add GitHub Secrets

### 2.1: Go to Your GitHub Repository

1. Go to: https://github.com/yourusername/callsync
2. Click **Settings** (top right)
3. Left sidebar: Click **Secrets and variables** → **Actions**

### 2.2: Create Secrets

Click **New repository secret** and add:

**Secret 1: AWS_ACCESS_KEY_ID**
- Name: `AWS_ACCESS_KEY_ID`
- Value: (paste your AKIA... from ~/.aws/credentials)
- Click **Add secret**

**Secret 2: AWS_SECRET_ACCESS_KEY**
- Name: `AWS_SECRET_ACCESS_KEY`
- Value: (paste your wJal... from ~/.aws/credentials)
- Click **Add secret**

**Secret 3: AWS_REGION** (optional)
- Name: `AWS_REGION`
- Value: `us-east-1`
- Click **Add secret**

### Result:
You should now see 3 secrets listed. ✓

---

## Step 3: Verify GitHub Actions are Enabled

1. Go to your repo
2. Click **Actions** tab (top menu)
3. You should see workflows:
   - ✓ Tests
   - ✓ Build
   - ✓ Deploy

If you don't see them, workflows are disabled. To enable:
1. Settings → Actions → General
2. Under "Actions permissions", select **"Allow all actions and reusable workflows"**
3. Click **Save**

---

## Step 4: Test the CI/CD Pipeline

### Test 1: Run tests on Pull Request

```bash
# Create a test branch
git checkout -b test/cicd-setup

# Make a small change
echo "# CI/CD is working!" >> README.md

# Commit and push
git add README.md
git commit -m "test: verify cicd setup"
git push origin test/cicd-setup

# Go to GitHub and create a Pull Request
# Watch the "Tests" workflow run automatically
```

Check: https://github.com/yourusername/callsync/pulls

You should see "Tests" workflow running. ✓

### Test 2: Merge to main and watch auto-deployment

```bash
# Merge the PR on GitHub (or locally)
git checkout main
git merge test/cicd-setup
git push origin main

# Watch deployments happen automatically:
# 1. Tests workflow (5 min)
# 2. Build workflow (10 min)
# 3. Deploy workflow (15 min)
```

Check: https://github.com/yourusername/callsync/actions

You should see all 3 workflows running. ✓

---

## Workflow Breakdown

### Workflow 1: Tests (Runs on PR & push)

**File:** `.github/workflows/test.yml`

**When it runs:**
- Every push to any branch
- Every pull request

**What it does:**
- Backend tests with PostgreSQL + Redis
- Frontend build & lint
- Mobile type checking
- Terraform validation
- Security scanning

**Time:** 15-20 minutes

**View results:** GitHub PR checks

### Workflow 2: Build (Runs on main merge)

**File:** `.github/workflows/build.yml`

**When it runs:**
- Only when tests pass
- Only on main branch

**What it does:**
- Builds backend Docker image
- Builds frontend Docker image
- Pushes to GitHub Container Registry (GHCR)

**Time:** 10-15 minutes

**View results:** Actions tab → Build workflow

### Workflow 3: Deploy (Runs on main merge)

**File:** `.github/workflows/deploy.yml`

**When it runs:**
- Only when build succeeds
- Only on main branch

**What it does:**
- Initializes Terraform
- Applies infrastructure changes
- Updates ECS service
- Runs smoke tests
- Health checks

**Time:** 20-30 minutes

**View results:** Actions tab → Deploy workflow

---

## Complete Deployment Flow

```
You push code to GitHub
    ↓
Workflow 1: Tests
├─ Backend tests
├─ Frontend build
├─ Mobile type check
├─ Terraform validate
└─ Security scan
    ↓
    All tests pass?
    ├─ YES → Continue to Build
    └─ NO → Fail, notify you
    ↓
Workflow 2: Build (if on main)
├─ Build backend image
├─ Build frontend image
└─ Push to GHCR
    ↓
Workflow 3: Deploy (if on main)
├─ Terraform apply
├─ Update ECS service
├─ Run smoke tests
└─ Verify health checks
    ↓
Your code is LIVE on AWS!
```

---

## Monitoring Deployments

### Watch in Real-Time

1. Go to: https://github.com/yourusername/callsync/actions
2. Click the latest workflow run
3. Click each job to see live logs

### View Logs

**Backend logs:**
```bash
aws logs tail /ecs/callsync-dev --follow
```

**Deployment logs:**
```bash
aws ecs describe-services --cluster callsync-dev --services callsync-api
```

**CloudWatch dashboard:**
https://console.aws.amazon.com/cloudwatch

---

## Troubleshooting CI/CD

### Workflow fails at "Configure AWS credentials"

**Problem:** GitHub Secrets not found
**Solution:**
1. Go to Settings → Secrets
2. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` exist
3. Re-run workflow

### Terraform apply fails

**Problem:** State file issues
**Solution:**
```bash
# Check S3 bucket was created
aws s3 ls | grep terraform

# Check DynamoDB table
aws dynamodb list-tables
```

### Docker push fails

**Problem:** ECR authentication
**Solution:**
- AWS credentials expire
- Regenerate access keys: https://console.aws.amazon.com/iam
- Update GitHub Secrets
- Re-run workflow

### ECS deployment fails

**Problem:** Service can't update
**Solution:**
```bash
# Check service status
aws ecs describe-services --cluster callsync-dev --services callsync-api

# Check task definition
aws ecs describe-task-definition --task-definition callsync-api

# View logs
aws logs tail /ecs/callsync-dev --follow
```

---

## Advanced: Manual Workflow Triggers

### Manually trigger deploy to staging

Edit `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Add this line
    inputs:
      environment:
        description: 'Environment'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
```

Then in GitHub Actions, you'll see "Run workflow" button. ✓

---

## Security Best Practices

### ✅ DO:
- ✓ Use GitHub Secrets for credentials
- ✓ Regenerate AWS keys periodically
- ✓ Use minimal IAM permissions (we used Admin for simplicity)
- ✓ Monitor Actions logs for errors
- ✓ Review PRs before merging

### ❌ DON'T:
- ✗ Commit credentials to git
- ✗ Share GitHub Secrets URLs
- ✗ Use permanent AWS credentials (use temporary STS if possible)
- ✗ Push to main without tests passing
- ✗ Ignore failed workflow notifications

---

## Checking Deployment Status

### In GitHub:
1. Go to **Actions** tab
2. Latest workflow shows status:
   - 🟡 Running
   - ✓ Passed
   - ✗ Failed

### In AWS:
1. Go to **CloudWatch**: https://console.aws.amazon.com/cloudwatch
2. View **Logs** → `/ecs/callsync-dev`
3. Check **ECS Cluster** for service status

### Via CLI:
```bash
# Deployment status
aws ecs describe-services --cluster callsync-dev --services callsync-api

# Recent logs
aws logs tail /ecs/callsync-dev --follow

# Task status
aws ecs list-tasks --cluster callsync-dev
```

---

## Development Workflow

### For new features:

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test locally
npm run dev  # or your local test

# 3. Push and create PR
git push origin feature/my-feature

# GitHub Actions automatically:
# ✓ Runs tests
# ✓ Checks build
# ✓ Comments on PR with results

# 4. Once approved, merge to main
# GitHub Actions automatically:
# ✓ Builds images
# ✓ Deploys to AWS
# ✓ Runs health checks

# 5. Verify deployment
curl http://ALB_DNS/health
```

---

## Summary

### ✅ You now have:

- [x] Local deployment: `DEPLOY_AUTOMATED.sh`
- [x] GitHub Secrets configured
- [x] Test workflow (runs on PR)
- [x] Build workflow (runs on main)
- [x] Deploy workflow (runs on main)
- [x] Automatic health checks
- [x] CloudWatch monitoring

### 📊 Deployment Pipeline:

```
Feature Branch → PR → Tests Pass → Merge to Main → Build → Deploy → Live!
```

### 🚀 Next Steps:

1. **Push code to GitHub:**
   ```bash
   git push origin main
   ```

2. **Watch deployments in Actions:**
   https://github.com/yourusername/callsync/actions

3. **Monitor in CloudWatch:**
   https://console.aws.amazon.com/cloudwatch

---

## Quick Reference

| Action | Command | Time |
|--------|---------|------|
| Local deploy | `./DEPLOY_AUTOMATED.sh` | 45 min |
| Run tests | `pytest tests/` | 5 min |
| View logs | `aws logs tail /ecs/callsync-dev --follow` | Live |
| Check deployment | https://github.com/.../actions | Live |
| Verify API | `curl http://ALB_DNS/health` | 1 sec |

---

**GitHub CI/CD is now fully configured!** 🚀

Push code → GitHub Actions handles everything → Your changes go live automatically!
