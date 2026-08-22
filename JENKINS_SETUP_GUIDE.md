# 🔧 Jenkins Pipeline Setup Guide

**Orchestrate all CallSync deployments from a single Jenkins dashboard.**

---

## 📋 Overview

The Jenkinsfile provides a unified pipeline that handles:
- ✅ Infrastructure status checks
- ✅ Starting AWS infrastructure
- ✅ Stopping AWS infrastructure
- ✅ Running tests (backend, frontend, mobile)
- ✅ Local deployment
- ✅ AWS deployment
- ✅ Health checks

**Supported Environments:** dev, staging, production

---

## 🚀 Quick Setup

### Step 1: Install Jenkins

**On Mac:**
```bash
brew install jenkins-lts
brew services start jenkins
```

**On Linux:**
```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
sudo systemctl start jenkins
```

**On Windows:**
Download from: https://www.jenkins.io/download/

### Step 2: Access Jenkins Dashboard
```
http://localhost:8080
```

Get initial password:
```bash
cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Step 3: Install Required Plugins

In Jenkins → Manage Jenkins → Plugin Manager → Available:
- Git
- Pipeline
- AWS Credentials
- Docker
- CloudBees Docker Build and Publish
- Email Extension Plugin (optional)

### Step 4: Add AWS Credentials

Jenkins → Manage Jenkins → Credentials → System → Global credentials:

1. Click "Add Credentials"
2. Kind: "Username with password"
3. Username: `aws-account-id`
4. Password: (your AWS Account ID)
5. ID: `aws-account-id`
6. Save

Repeat for:
- `aws-access-key-id` (your AKIA...)
- `aws-secret-access-key` (your wJal...)

### Step 5: Create New Pipeline Job

1. Jenkins home → New Item
2. Name: `CallSync`
3. Type: `Pipeline`
4. Click OK

### Step 6: Configure Pipeline

In the job configuration:

**Definition:** Pipeline script from SCM
**SCM:** Git
**Repository URL:** https://github.com/nighthawk369/callsync.git
**Credentials:** (select your git credentials or leave blank for public)
**Branch:** */main
**Script Path:** Jenkinsfile

Click Save

---

## 📊 Pipeline Actions

### CHECK_STATUS
```
Checks:
✓ AWS credentials
✓ ECS cluster status
✓ RDS database status
✓ ECS service running tasks
✓ API health endpoint
✓ Estimated monthly cost
```

**Time:** ~1 minute

### START_INFRASTRUCTURE
```
Creates:
✓ VPC with subnets
✓ RDS PostgreSQL database
✓ ElastiCache Redis
✓ ECS Fargate cluster
✓ Application Load Balancer
✓ Security groups
✓ CloudWatch logs
```

**Time:** ~20 minutes

### STOP_INFRASTRUCTURE
```
Destroys:
✗ All AWS resources
✗ ECS service
✗ RDS instance
✗ Load Balancer

Preserves:
✓ Terraform state
✓ RDS snapshots
✓ Configuration
```

**Time:** ~10 minutes

### RUN_TESTS (Parallel)
```
Backend Tests:
✓ pytest integration tests
✓ API endpoint validation
✓ Multi-tenancy verification

Frontend Build:
✓ npm install
✓ Next.js build
✓ TypeScript check

Mobile Build:
✓ npm install
✓ TypeScript validation
✓ Expo config check
```

**Time:** ~10 minutes

### DEPLOY_LOCAL
```
Executes:
✓ Bootstrap Terraform
✓ Initialize main Terraform
✓ Deploy infrastructure
✓ Build Docker images
✓ Update ECS service
✓ Run health checks
✓ Save deployment info
```

**Time:** ~45 minutes

### DEPLOY_TO_AWS
```
Performs:
✓ Build Docker images
✓ Push to ECR
✓ Update ECS service
✓ Force new deployment
✓ Health checks
```

**Time:** ~15 minutes

### FULL_CYCLE
```
Runs in sequence:
1. CHECK_STATUS (1 min)
2. START_INFRASTRUCTURE (20 min)
3. RUN_TESTS (10 min parallel)
4. DEPLOY_LOCAL (45 min)
5. HEALTH_CHECK (5 min)
```

**Total Time:** ~80 minutes

---

## 🎯 Using the Pipeline

### From Jenkins Dashboard

1. Go to: http://localhost:8080
2. Click `CallSync` job
3. Click `Build with Parameters`
4. Select:
   - **ENVIRONMENT:** dev, staging, or production
   - **ACTION:** Choose action (see above)
5. Click `Build`
6. Monitor progress in Build Output

### Viewing Build Output

1. Click the build number (e.g., `#1`)
2. Click `Console Output`
3. Watch real-time execution

### Common Workflows

**Developer Morning Routine:**
```
Action: CHECK_STATUS
  ↓ (infrastructure stopped)
Action: START_INFRASTRUCTURE
  ↓ (wait 20 min)
Action: DEPLOY_LOCAL
  ↓ (wait 45 min)
Action: FULL_CYCLE (next day)
```

**Before Demo:**
```
Action: CHECK_STATUS
  ↓ (verify running)
Action: RUN_TESTS
  ↓ (verify all tests pass)
```

**End of Day:**
```
Action: STOP_INFRASTRUCTURE
  ↓ (saves costs)
```

---

## 📈 Pipeline Stages Detail

```
Pipeline: CallSync
├── Initialize
│   └── Verify AWS credentials
│
├── Check Status (if action includes)
│   └── Run INFRASTRUCTURE_STATUS.sh
│
├── Start Infrastructure (if requested)
│   └── Run START_INFRASTRUCTURE.sh
│
├── Stop Infrastructure (if requested)
│   └── Run STOP_INFRASTRUCTURE.sh
│
├── Run Tests (parallel if not stopping)
│   ├── Backend Tests
│   │   └── pytest integration tests
│   ├── Frontend Build
│   │   └── npm run build
│   └── Mobile Build
│       └── TypeScript validation
│
├── Deploy Local (if requested)
│   └── Run DEPLOY_AUTOMATED.sh
│
├── Deploy to AWS (if requested)
│   ├── Build Docker image
│   ├── Push to ECR
│   └── Update ECS service
│
├── Health Check (unless stopping)
│   ├── Run INFRASTRUCTURE_STATUS.sh
│   └── Test API /health endpoint
│
└── Post Actions
    ├── On Success: Archive artifacts
    ├── On Failure: Send notification
    └── Always: Pipeline summary
```

---

## 🔐 Security Setup

### 1. Secure Jenkins

```bash
# Change default port (optional)
# Edit: /etc/default/jenkins
# JENKINS_PORT=8080 → JENKINS_PORT=9000

# Enable authentication
Jenkins → Configure Global Security
→ Authentication: Jenkins' own user database
→ Create admin user
```

### 2. AWS Credentials

**Never commit credentials to git!**

Store in Jenkins Credentials:
- Jenkins → Manage Jenkins → Credentials
- Use masking in logs
- Rotate keys regularly

### 3. SSH Key Setup (optional)

For GitHub pull via SSH:
```bash
# Generate SSH key (if not exists)
ssh-keygen -t ed25519 -f ~/.ssh/jenkins

# Add to GitHub deploy keys
# Settings → Deploy keys → Add Key
cat ~/.ssh/jenkins.pub
```

---

## 📊 Monitoring & Notifications

### View Build History
```
Jenkins → CallSync → Build History
```

Shows:
- Build number
- Status (✓ success, ✗ failure)
- Duration
- Parameters used

### Email Notifications (Optional)

Uncomment in Jenkinsfile:
```groovy
post {
    success {
        emailext(
            subject: "✅ CallSync Pipeline Success",
            body: "Pipeline completed successfully",
            to: "team@example.com"
        )
    }
    failure {
        emailext(
            subject: "❌ CallSync Pipeline Failed",
            body: "Pipeline failed. Check logs.",
            to: "team@example.com"
        )
    }
}
```

### Slack Notifications (Optional)

Add to pipeline:
```groovy
post {
    always {
        slackSend(
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
            message: "${env.JOB_NAME} - ${currentBuild.displayName} ${currentBuild.result}",
            webhookUrl: "${SLACK_WEBHOOK}"
        )
    }
}
```

---

## 🛠️ Troubleshooting

### Pipeline Won't Start

**Problem:** "Permission denied" on scripts
```bash
# Fix: Make scripts executable
chmod +x START_INFRASTRUCTURE.sh
chmod +x STOP_INFRASTRUCTURE.sh
chmod +x INFRASTRUCTURE_STATUS.sh
chmod +x DEPLOY_AUTOMATED.sh
```

### AWS Credentials Not Found

**Problem:** "InvalidClientTokenId" in logs
```bash
# Fix: Verify Jenkins credentials
Jenkins → Credentials → Check IDs match Jenkinsfile
```

### Docker Build Fails

**Problem:** "Cannot connect to Docker daemon"
```bash
# Fix: Install Docker
brew install docker  # Mac
sudo apt-get install docker.io  # Linux

# Add Jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Pipeline Hangs

**Problem:** Pipeline stuck on infrastructure deployment
```bash
# Check infrastructure status
./INFRASTRUCTURE_STATUS.sh

# Check Terraform logs
cd infrastructure/terraform/aws
terraform show
```

---

## 🔄 CI/CD Integration

### Jenkins + GitHub

When code is pushed:
```
GitHub → Webhook → Jenkins
↓
Jenkins triggers pipeline
↓
Runs tests, builds, deploys
```

To setup webhook:
```
GitHub Repo Settings → Webhooks → Add webhook
Payload URL: http://jenkins.example.com/github-webhook/
Events: Push events
```

### Jenkins + Docker Registry

Pipeline automatically:
1. Builds Docker images
2. Pushes to ECR
3. Updates ECS service

No manual Docker commands needed!

---

## 📋 Parameter Reference

| Parameter | Options | Default | Effect |
|-----------|---------|---------|--------|
| ENVIRONMENT | dev, staging, production | dev | Where to deploy |
| ACTION | CHECK_STATUS, START, STOP, DEPLOY_LOCAL, etc. | N/A | What to execute |

---

## 🎯 Complete Workflow Example

### Day 1
```
1. Open http://localhost:8080
2. Click CallSync → Build with Parameters
3. ENVIRONMENT: dev
4. ACTION: CHECK_STATUS
   Result: Infrastructure STOPPED

5. ACTION: START_INFRASTRUCTURE
   Wait: 20 minutes
   Result: API ready at http://alb-dns/

6. ACTION: DEPLOY_LOCAL
   Wait: 45 minutes
   Result: Application deployed
```

### Day 2-4
```
Each morning:
1. ACTION: CHECK_STATUS (verify running)
2. Push code to GitHub (tests run automatically)

Each evening:
1. ACTION: STOP_INFRASTRUCTURE
   Saves costs
```

### Day 5
```
1. ACTION: FULL_CYCLE
   - Checks status
   - Starts infrastructure
   - Runs all tests
   - Deploys locally
   - Health checks
   Total: 80 minutes
```

---

## 📞 Support

**Jenkins not starting?**
```bash
# Check logs
tail -f /var/log/jenkins/jenkins.log

# Restart
brew services restart jenkins  # Mac
sudo systemctl restart jenkins  # Linux
```

**Pipeline fails on credential error?**
```bash
# Verify credentials in Jenkins UI
Jenkins → Credentials → System → Global credentials
```

---

**Jenkins Pipeline Ready!** 🚀

Orchestrate all deployments from one place.
