# 🔄 CallSync - Infrastructure Lifecycle Management

**Start and stop your AWS infrastructure on demand to optimize costs.**

---

## 📊 Cost Optimization

### Running (24/7)
```
Dev Environment: $32/month
Monthly cost: active
```

### Stopped (0/7)
```
Dev Environment: $0/month (only S3 storage: ~$1)
Monthly cost: minimal
```

**By stopping infrastructure when not in use, you can reduce monthly costs by 97%!**

---

## 🚀 Quick Start

### Check Current Status
```bash
./INFRASTRUCTURE_STATUS.sh
```

Shows:
- ✓ Is infrastructure running?
- ✓ ECS cluster status
- ✓ RDS database status
- ✓ API health check
- ✓ Estimated monthly cost

### Start Infrastructure
```bash
./START_INFRASTRUCTURE.sh
```

Deploys:
- VPC with subnets
- RDS PostgreSQL
- ElastiCache Redis
- ECS cluster & service
- Application Load Balancer
- Security groups

**Takes ~20 minutes**

### Stop Infrastructure
```bash
./STOP_INFRASTRUCTURE.sh
```

Removes all resources (saves costs) but keeps:
- ✓ Terraform state (in S3)
- ✓ Database snapshots
- ✓ Configuration

**Takes ~10 minutes**

---

## 📋 Complete Workflow

### Day 1: Start Development
```bash
# Check status
./INFRASTRUCTURE_STATUS.sh
# Output: Infrastructure is STOPPED

# Start infrastructure
./START_INFRASTRUCTURE.sh
# Waits ~20 minutes...

# Now you can deploy and develop
./DEPLOY_AUTOMATED.sh
```

### During Development
```bash
# Monitor infrastructure
./INFRASTRUCTURE_STATUS.sh

# View logs
aws logs tail /ecs/callsync-dev --follow

# Check costs
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31 --granularity MONTHLY --metrics "UnblendedCost"
```

### End of Day: Stop Infrastructure
```bash
# Stop when done developing
./STOP_INFRASTRUCTURE.sh
# Answer: destroy everything

# Infrastructure is now stopped
# You only pay for S3 storage (~$1/month)
```

### Next Day: Resume Work
```bash
# Start infrastructure again
./START_INFRASTRUCTURE.sh

# Deploy changes
./DEPLOY_AUTOMATED.sh

# Continue developing
```

---

## 🎯 Three Scripts

### 1. INFRASTRUCTURE_STATUS.sh
**Purpose:** Check if infrastructure is running

**What it does:**
```
✓ Verifies AWS credentials
✓ Checks ECS cluster status
✓ Checks RDS database status
✓ Checks ECS service status
✓ Tests API health
✓ Shows current API URL
✓ Estimates monthly cost
```

**Usage:**
```bash
./INFRASTRUCTURE_STATUS.sh
```

**Output:**
```
✓ ECS Cluster ACTIVE
✓ RDS Database available
✓ ECS Service ACTIVE
✓ Running tasks: 1
✓ API: http://callsync-alb-xxxxx.us-east-1.elb.amazonaws.com
✓ API is responding (HTTP 200)

Infrastructure is RUNNING
Current monthly cost: ~$32
```

---

### 2. START_INFRASTRUCTURE.sh
**Purpose:** Deploy all AWS resources

**What it does:**
```
✓ Verifies AWS credentials
✓ Shows Terraform plan
✓ Asks for confirmation
✓ Deploys infrastructure (~20 min)
✓ Retrieves API endpoint
✓ Saves deployment info to infrastructure-running.txt
```

**Usage:**
```bash
./START_INFRASTRUCTURE.sh
```

**Deployment time:** 15-20 minutes

**Creates:**
- VPC, subnets, security groups
- RDS PostgreSQL database
- ElastiCache Redis
- ECS Fargate cluster
- Application Load Balancer
- CloudWatch logs

**Output:**
```
✓ Infrastructure Started!

Your CallSync API:
  http://callsync-alb-xxxxx.us-east-1.elb.amazonaws.com

Next steps:
  1. Deploy application: ./DEPLOY_AUTOMATED.sh
  2. Monitor logs: aws logs tail /ecs/callsync-dev --follow
  3. Stop when done: ./STOP_INFRASTRUCTURE.sh
```

---

### 3. STOP_INFRASTRUCTURE.sh
**Purpose:** Destroy all AWS resources (saves costs)

**What it does:**
```
⚠️  Shows warning about data loss
✓ Asks for double confirmation
✓ Verifies AWS credentials
✓ Destroys all resources (~10 min)
✓ Cleans up local files
```

**Usage:**
```bash
./STOP_INFRASTRUCTURE.sh
# Answer: destroy everything
```

**Destruction time:** 10 minutes

**Removes:**
- ✗ ECS cluster & service
- ✗ RDS database
- ✗ ElastiCache Redis
- ✗ Load Balancer
- ✗ VPC & security groups

**Keeps (recoverable):**
- ✓ Terraform state (S3)
- ✓ RDS snapshots (automatic backups)
- ✓ Configuration

**Cost:** ~$0/month (only S3 storage ~$1)

---

## 💡 Use Cases

### Use Case 1: Development
```bash
Monday morning:
  ./START_INFRASTRUCTURE.sh

Monday-Friday:
  ./INFRASTRUCTURE_STATUS.sh  # Check status
  ./DEPLOY_AUTOMATED.sh       # Deploy code

Friday evening:
  ./STOP_INFRASTRUCTURE.sh

Cost: 5 days × $32 ÷ 30 = ~$5.33/month
```

### Use Case 2: Demo
```bash
Before demo:
  ./START_INFRASTRUCTURE.sh

Demo to stakeholders:
  ./INFRASTRUCTURE_STATUS.sh  # Show API is up
  curl http://ALB_DNS/docs    # Show API docs

After demo:
  ./STOP_INFRASTRUCTURE.sh

Cost: 2 hours × $32 ÷ 30 ÷ 24 = ~$0.09
```

### Use Case 3: Always-On Production
```bash
# Keep infrastructure running (don't use STOP_INFRASTRUCTURE.sh)

Cost: 30 days × $32 = $32/month
(or $416/month for production with 3 AZs)
```

---

## 🔍 Monitoring During Runtime

### Check Infrastructure Status
```bash
./INFRASTRUCTURE_STATUS.sh
```

### View Live Logs
```bash
aws logs tail /ecs/callsync-dev --follow
```

### Check Service Health
```bash
aws ecs describe-services --cluster callsync-dev --services callsync-api
```

### Get API Endpoint
```bash
terraform -chdir=infrastructure/terraform/aws output -raw alb_dns_name
```

### Test API
```bash
ALB_DNS=$(terraform -chdir=infrastructure/terraform/aws output -raw alb_dns_name)
curl http://$ALB_DNS/health
curl http://$ALB_DNS/docs
```

---

## 📈 Cost Scenarios

### Scenario 1: Development Only (Business Days)
```
Mon-Fri: Infrastructure running = 5 × 8 hours
Mon-Fri: Infrastructure stopped = 5 × 16 hours
Weekend: Infrastructure stopped = 48 hours

Cost per week: (5 × 8 ÷ 24 ÷ 7) × $32 = ~$7.62/month
Savings: 76% reduction
```

### Scenario 2: Continuous Development
```
24/7 running: 30 days = $32/month
Cost per month: $32
```

### Scenario 3: Testing Only (2 Hours Daily)
```
2 hours/day × 30 days = 60 hours/month
Cost: (60 ÷ 24 ÷ 30) × $32 = ~$0.27/month
Savings: 99% reduction
```

---

## ⚠️ Important Notes

### Data Safety
- ✓ RDS automated backups enabled
- ✓ Backups preserved when infrastructure stopped
- ✓ Can restore from snapshots
- ✓ Terraform state always preserved

### Terraform State
- ✓ Stored in S3 (durable)
- ✓ DynamoDB locking prevents corruption
- ✓ Safe to stop/start infrastructure repeatedly
- ✓ Never loses state

### Re-deployment
- ✓ Can start/stop unlimited times
- ✓ Same infrastructure each time
- ✓ Configuration preserved
- ✓ Just run `./START_INFRASTRUCTURE.sh` again

### DNS/IP Changes
- ⚠️ ALB DNS name changes on each start
- ⚠️ RDS endpoint might change
- ⚠️ Save new endpoints to `infrastructure-running.txt`
- ⚠️ Update your DNS records if using custom domain

---

## 🚨 Emergency Procedures

### Infrastructure Won't Start
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket exists
aws s3 ls | grep terraform

# Check DynamoDB table
aws dynamodb list-tables

# Check Terraform state
aws s3 ls s3://callsync-terraform-state-ACCOUNT_ID/
```

### Infrastructure Won't Stop
```bash
# Manually destroy via AWS Console
# Or force destroy via Terraform
cd infrastructure/terraform/aws
terraform destroy -auto-approve

# This is dangerous, use only if scripts fail
```

### Lost API Endpoint
```bash
# Get from Terraform state
terraform -chdir=infrastructure/terraform/aws output -raw alb_dns_name

# Or check infrastructure-running.txt
cat infrastructure-running.txt
```

---

## 📊 CLI Summary

| Command | Time | Action |
|---------|------|--------|
| `./INFRASTRUCTURE_STATUS.sh` | 1 min | Check status |
| `./START_INFRASTRUCTURE.sh` | 20 min | Deploy all resources |
| `./STOP_INFRASTRUCTURE.sh` | 10 min | Destroy all resources |
| `./DEPLOY_AUTOMATED.sh` | 45 min | Deploy application code |

---

## 🎯 Recommended Workflow

```
Week 1:
  Mon: ./START_INFRASTRUCTURE.sh → ./DEPLOY_AUTOMATED.sh
  Tue-Thu: Code changes pushed to GitHub (auto-deploys)
  Fri: ./STOP_INFRASTRUCTURE.sh

Cost: ~$5/month

Whenever needed:
  ./START_INFRASTRUCTURE.sh → Demo/test
  ./STOP_INFRASTRUCTURE.sh → Stop costs
```

---

**Infrastructure Lifecycle Management Ready!** 🚀

Optimize your costs by starting and stopping infrastructure on demand.
