# 🚀 CallSync - Complete Deployment Guide

**Everything you need to deploy CallSync from start to finish.**

---

## 📊 Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PHASE 1: LOCAL SETUP (You do this once)                       │
│  ├─ Configure AWS credentials (aws configure)                  │
│  ├─ Run DEPLOY_AUTOMATED.sh                                    │
│  │  ├─ Bootstrap: Create S3 + DynamoDB (Terraform)            │
│  │  ├─ Main: Deploy all infrastructure (Terraform)             │
│  │  ├─ Build: Docker images                                    │
│  │  └─ Deploy: ECS service                                     │
│  └─ Result: ✓ CallSync live on AWS                             │
│                                                                 │
│  PHASE 2: GITHUB CI/CD SETUP (You do this once)                │
│  ├─ Add AWS credentials to GitHub Secrets                      │
│  ├─ Enable GitHub Actions                                      │
│  └─ Result: ✓ Auto-deployment on push to main                  │
│                                                                 │
│  PHASE 3: ONGOING DEVELOPMENT (Repeating)                      │
│  ├─ Create feature branch                                      │
│  ├─ Make changes & test locally                                │
│  ├─ Push to GitHub                                             │
│  │  └─ GitHub Actions: Tests run (PR checks)                   │
│  ├─ Merge to main                                              │
│  │  ├─ GitHub Actions: Tests run                               │
│  │  ├─ GitHub Actions: Build Docker images                     │
│  │  └─ GitHub Actions: Deploy to AWS                           │
│  └─ Result: ✓ Changes live in production                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Start (5 Minutes)

### 1️⃣ **Verify AWS CLI is configured**
```bash
aws sts get-caller-identity
# Should show your AWS account info
```

### 2️⃣ **Run local deployment**
```bash
cd /Users/nikhilpanwar/Coding/first_product
./DEPLOY_AUTOMATED.sh
# Takes ~45 minutes
# Everything is automated!
```

### 3️⃣ **Save the output**
The script creates `deployment-info.txt` with your URLs.

That's it! CallSync is now live on AWS. ✓

---

## 📋 Phase 1: Local Deployment (45 Minutes)

### What You Need
- [x] AWS credentials configured (`aws configure`)
- [x] Docker installed
- [x] Terraform installed
- [x] Git configured

### What DEPLOY_AUTOMATED.sh Does

**Step 1: Bootstrap (Creates S3 + DynamoDB)**
```
Terraform (bootstrap/) creates:
  ✓ S3 bucket for state (versioned, encrypted)
  ✓ DynamoDB table for locking
```

**Step 2: Initialize Main Terraform**
```
Terraform (aws/) initializes with S3 backend
  ✓ Uses the bucket created in Step 1
```

**Step 3: Deploy Infrastructure**
```
Terraform applies configuration:
  ✓ VPC with subnets
  ✓ RDS PostgreSQL database
  ✓ ElastiCache Redis
  ✓ ECS cluster & service
  ✓ Application Load Balancer
  ✓ Security groups
  Time: 15-20 minutes
```

**Step 4: Build Docker Images**
```
Docker builds and pushes:
  ✓ Backend image → ECR
  ✓ All code containerized
  Time: 5 minutes
```

**Step 5: Deploy to ECS**
```
AWS updates service:
  ✓ Pulls new images
  ✓ Updates running tasks
  ✓ Health checks pass
  Time: 5 minutes
```

**Step 6: Verify**
```
Tests confirm:
  ✓ API responding
  ✓ Health checks pass
  ✓ All systems operational
```

### Run It

```bash
cd /Users/nikhilpanwar/Coding/first_product
chmod +x DEPLOY_AUTOMATED.sh
./DEPLOY_AUTOMATED.sh
```

Follow the prompts. It will:
- ✓ Verify prerequisites
- ✓ Show confirmation before deploying
- ✓ Display progress
- ✓ Save deployment info

### Result

File: `deployment-info.txt`
```
API: http://callsync-alb-xxxxx.us-east-1.elb.amazonaws.com
Docs: http://callsync-alb-xxxxx.us-east-1.elb.amazonaws.com/docs
Health: http://callsync-alb-xxxxx.us-east-1.elb.amazonaws.com/health
```

---

## 🔄 Phase 2: GitHub CI/CD Setup (10 Minutes)

### Step 1: Get AWS Credentials

```bash
# Your credentials are stored locally here:
cat ~/.aws/credentials

# You'll see:
# [default]
# aws_access_key_id = AKIA...
# aws_secret_access_key = wJal...

# Save these values
```

### Step 2: Add to GitHub Secrets

1. Go to your GitHub repo
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add 3 secrets:

**Secret 1:**
- Name: `AWS_ACCESS_KEY_ID`
- Value: (your AKIA...)

**Secret 2:**
- Name: `AWS_SECRET_ACCESS_KEY`
- Value: (your wJal...)

**Secret 3:**
- Name: `AWS_REGION`
- Value: `us-east-1`

### Step 3: Enable GitHub Actions (if disabled)

1. Settings → **Actions** → **General**
2. Select **"Allow all actions"**
3. Save

### Step 4: Test It

```bash
# Create test branch
git checkout -b test/cicd

# Make a change
echo "Testing CI/CD" >> README.md

# Push and create PR
git add README.md
git commit -m "test: cicd"
git push origin test/cicd

# Go to GitHub → Create Pull Request
# Watch "Tests" workflow run automatically
```

### Result

Now GitHub Actions runs:
- ✓ Tests on every PR
- ✓ Build on main merge
- ✓ Deploy on build success

---

## 🔐 Phase 3: Ongoing Development

### Feature Development Workflow

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Test locally (optional)
cd backend && python -m pytest tests/ && cd ..

# 4. Commit and push
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature

# GitHub Actions automatically runs:
# ✓ Backend tests
# ✓ Frontend build
# ✓ Mobile type check
# ✓ Security scan
# → Check PR for results
```

### Merge and Deploy

```bash
# 1. Go to GitHub
# 2. Create Pull Request
# 3. Review (tests must pass)
# 4. Merge to main

# GitHub Actions automatically:
# ✓ Runs tests again
# ✓ Builds Docker images (5 min)
# ✓ Deploys to AWS (10 min)
# ✓ Runs smoke tests
# ✓ Verifies health checks

# Your changes are LIVE!
```

---

## 📊 Three Workflows Explained

### Workflow 1: Tests

**File:** `.github/workflows/test.yml`

**Triggers:**
- Every push (any branch)
- Every PR

**What it does:**
- Backend tests with PostgreSQL + Redis
- Frontend build & lint
- Mobile type checking
- Terraform validation
- Container image scanning

**Time:** 15-20 minutes

**Status:** Check PR for "Details" link

### Workflow 2: Build

**File:** `.github/workflows/build.yml`

**Triggers:**
- Only on main branch
- Only if tests pass

**What it does:**
- Builds backend Docker image
- Builds frontend Docker image
- Pushes to GitHub Container Registry

**Time:** 10-15 minutes

**Status:** Actions tab → Build workflow

### Workflow 3: Deploy

**File:** `.github/workflows/deploy.yml`

**Triggers:**
- Only on main branch
- Only if build succeeds

**What it does:**
- Initializes Terraform with S3 backend
- Applies infrastructure changes
- Updates ECS service
- Runs smoke tests
- Health checks

**Time:** 20-30 minutes

**Status:** Actions tab → Deploy workflow

---

## 🛠️ Infrastructure (What Gets Created)

### By Bootstrap Terraform
```
✓ S3 bucket (terraform-state)
  - Versioning enabled
  - Encryption enabled
  - Public access blocked
  - Prevent destroy enabled

✓ DynamoDB table (terraform-locks)
  - Partition key: LockID
  - On-demand billing
  - Prevent destroy enabled
```

### By Main Terraform
```
✓ VPC
  - Public subnets
  - Private subnets
  - Internet Gateway
  - NAT Gateway

✓ RDS
  - PostgreSQL 15
  - t4g.micro instance
  - 20GB storage
  - Automated backups

✓ ElastiCache
  - Redis 7
  - t4g.micro instance
  - In-memory cache

✓ ECS
  - Fargate cluster
  - Task definition
  - Service with scaling

✓ Application Load Balancer
  - Port 80 & 443
  - Health checks
  - Auto-scaling

✓ Security Groups
  - ALB: 0.0.0.0:80,443
  - API: from ALB only
  - RDS: from API only
  - Redis: from API only
```

### Cost
- Dev: ~$32/month
- Staging: ~$107/month
- Production: ~$416/month (with Reserved Instances)

---

## 🔍 Monitoring & Troubleshooting

### View Deployment Progress

**In GitHub:**
```
https://github.com/yourusername/callsync/actions
→ Click latest workflow run
→ Click each job for logs
```

**In AWS Console:**
```
CloudWatch → Logs → /ecs/callsync-dev
→ Watch live logs
```

**Via CLI:**
```bash
# View logs
aws logs tail /ecs/callsync-dev --follow

# Check service status
aws ecs describe-services --cluster callsync-dev --services callsync-api

# Check task status
aws ecs list-tasks --cluster callsync-dev
```

### Common Issues

**Workflow fails at "Configure AWS credentials"**
- Check GitHub Secrets exist
- Verify secret names are exact
- Re-run workflow

**Terraform apply fails**
- Check S3 bucket exists: `aws s3 ls | grep terraform`
- Check DynamoDB table: `aws dynamodb list-tables`
- Check AWS credentials haven't expired

**Docker push fails**
- Regenerate AWS keys if expired
- Update GitHub Secrets
- Re-run workflow

**API not responding**
```bash
# Check ECS task logs
aws logs tail /ecs/callsync-dev --follow

# Check task definition
aws ecs describe-task-definition --task-definition callsync-api

# Check service has running tasks
aws ecs list-tasks --cluster callsync-dev
```

---

## 📚 Reference Documents

| Document | Purpose |
|----------|---------|
| AWS_SETUP_COMPLETE_GUIDE.md | AWS UI step-by-step (if new to AWS) |
| GITHUB_CICD_SETUP.md | GitHub Secrets & Actions guide |
| DEPLOYMENT_READY.md | Manual deployment steps |
| DEPLOYMENT_CHECKLIST.md | Detailed checklist |
| QUICK_REFERENCE.md | Command cheatsheet |

---

## 🎉 Success Criteria

✅ **Local Deployment Successful When:**
- [ ] DEPLOY_AUTOMATED.sh completes without errors
- [ ] deployment-info.txt created with URLs
- [ ] `curl http://ALB_DNS/health` returns 200
- [ ] CloudWatch logs show ECS activity
- [ ] API docs accessible at http://ALB_DNS/docs

✅ **GitHub CI/CD Working When:**
- [ ] Tests run on PR automatically
- [ ] Build succeeds on main merge
- [ ] Deploy succeeds on build success
- [ ] Changes appear on API after 30 minutes

---

## 🚀 Next Steps

### Week 1: Stabilize
- Monitor logs for errors
- Run load tests
- Verify cost is on track ($32/month)

### Week 2: Test
- Test signup/login flow
- Test CRM features
- Create sample data

### Week 3+: Enhance
- Deploy staging environment
- Implement Phase 11 (Calendar Integration)
- Add CRM integrations

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Don't know where to start | Start with Phase 1 above |
| AWS credentials not working | Run `aws configure` |
| Workflow not running | Enable Actions in GitHub Settings |
| Deployment failing | Check `aws logs tail /ecs/callsync-dev --follow` |
| Don't have AWS account | Read AWS_SETUP_COMPLETE_GUIDE.md |
| Can't find GitHub Secrets | GitHub Settings → Secrets and variables → Actions |

---

## 📋 Checklist

### Before Local Deployment
- [ ] AWS credentials configured (`aws sts get-caller-identity` works)
- [ ] Docker installed (`docker --version` works)
- [ ] Terraform installed (`terraform --version` works)
- [ ] Git configured

### During Local Deployment
- [ ] DEPLOY_AUTOMATED.sh runs without errors
- [ ] Infrastructure deploys successfully (15-20 min)
- [ ] Docker images built and pushed
- [ ] ECS service updated
- [ ] Health checks pass

### Before GitHub CI/CD
- [ ] GitHub Secrets configured (3 secrets)
- [ ] GitHub Actions enabled
- [ ] Pushed code to GitHub

### After GitHub CI/CD Setup
- [ ] Tests run on PR
- [ ] Build succeeds on main
- [ ] Deploy succeeds
- [ ] Code appears on API

---

## 💡 Tips & Tricks

```bash
# Watch deployment progress
watch -n 5 'aws ecs describe-services --cluster callsync-dev --services callsync-api'

# View last 100 log lines
aws logs tail /ecs/callsync-dev --max-items 100

# Get your API URL quickly
terraform output -raw alb_dns_name

# Check how much money you're spending
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics "UnblendedCost"

# SSH into running task (if needed)
aws ecs describe-tasks --cluster callsync-dev --tasks $(aws ecs list-tasks --cluster callsync-dev --query 'taskArns[0]' --output text)
```

---

**You now have a complete, production-grade CI/CD pipeline!** 🚀

Local deployment: `./DEPLOY_AUTOMATED.sh`
GitHub deployment: Push to main
Always live on AWS!
