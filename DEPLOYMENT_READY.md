# ✅ Deployment Ready - Complete Pipeline & Test Suite

## What's Been Prepared

### 1. ✅ GitHub Actions CI/CD Pipelines (`.github/workflows/`)

**test.yml** — Runs on every PR and push
- Backend tests with PostgreSQL + Redis
- Frontend build & lint
- Mobile lint & type checking  
- Terraform validation
- Security scanning

**build.yml** — Builds Docker images on main branch
- Backend Docker image → ECR
- Frontend Docker image → ECR
- Cache optimization

**deploy.yml** — Deploys to AWS
- Terraform infrastructure
- ECS service updates
- Smoke tests
- Supports dev & staging environments

### 2. ✅ Integration Tests

**Backend** (`backend/tests/test_integration.py`)
- Complete user flow: signup → login → CRM
- Multi-tenancy isolation verification
- Business type configuration testing
- Error handling & validation

**Frontend** (`frontend/tests/flow.test.tsx`)
- Authentication flow
- Business type selector
- API integration
- Error handling
- State persistence

**Mobile** (`mobile/tests/flow.test.ts`)
- Signup & login flow
- Contact management
- Navigation state
- Offline scenarios
- Conversation creation

### 3. ✅ Load Testing

**k6 Script** (`tests/load/api_load.js`)
- Ramps up to 100 concurrent users
- Tests auth & CRM endpoints
- Measures response times & error rates
- Customizable thresholds

### 4. ✅ Deployment Checklist

**DEPLOYMENT_CHECKLIST.md**
- Pre-deployment requirements
- 8-phase deployment guide
- Local testing procedures
- AWS deployment steps
- Monitoring setup
- Rollback procedures

### 5. ✅ Terraform Infrastructure

Already configured in `infrastructure/terraform/aws/`:
- VPC with subnets
- RDS PostgreSQL
- ElastiCache Redis
- ECS cluster
- Application Load Balancer
- Security groups
- Auto-scaling

---

## 🚀 Ready to Deploy? Follow These Steps

### Step 1: Pre-Deployment Setup (30 min)

```bash
# 1. Create AWS Account if needed
# 2. Create IAM user with programmatic access

# 3. Configure AWS locally
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# 4. Verify AWS credentials
aws sts get-caller-identity

# 5. Create S3 bucket for Terraform state
aws s3 mb s3://ai-voice-sms-terraform-state-$(date +%s) --region us-east-1
# Save the bucket name for next step

# 6. Create DynamoDB table for Terraform state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### Step 2: Configure GitHub Secrets (10 min)

In GitHub repository settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID = (from aws configure)
AWS_SECRET_ACCESS_KEY = (from aws configure)
```

### Step 3: Initialize Terraform (10 min)

```bash
cd infrastructure/terraform/aws

# Update backend config with your bucket name
# Edit main.tf or create backend.tf:
cat > backend.tf << 'BACKEND'
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "ai-voice-sms/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}
BACKEND

# Initialize
terraform init

# Validate
terraform validate
```

### Step 4: Deploy Dev Environment (20 min)

```bash
# From infrastructure/terraform/aws/

# Plan the deployment
terraform plan \
  -var-file="environments/dev-ultra-optimized.tfvars" \
  -out=tfplan

# Review the output
cat tfplan

# Apply
terraform apply tfplan

# Get outputs (save these!)
terraform output -json > outputs.json
cat outputs.json
```

**Expected output:**
- VPC ID
- RDS endpoint
- ElastiCache endpoint
- ECS cluster name
- ALB DNS name

### Step 5: Run Local Tests (15 min)

```bash
# 1. Backend tests
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-optimized.txt

# Setup test database
export DATABASE_URL="postgresql://user:password@localhost/aivoicesms_test"
alembic upgrade head

# Run integration tests
python -m pytest tests/test_integration.py -v

# 2. Frontend build
cd ../frontend
npm install
npm run build

# 3. Mobile
cd ../mobile
npm install
npx expo export --dry-run --platform all
```

### Step 6: Deploy Application to ECS (20 min)

```bash
# 1. Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 3. Create ECR repositories
aws ecr create-repository --repository-name ai-voice-sms-api --region us-east-1 || true
aws ecr create-repository --repository-name ai-voice-sms-frontend --region us-east-1 || true

# 4. Build & push backend
cd backend
docker build -t ai-voice-sms-api:latest .
docker tag ai-voice-sms-api:latest \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms-api:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms-api:latest

# 5. Build & push frontend
cd ../frontend
docker build -t ai-voice-sms-frontend:latest .
docker tag ai-voice-sms-frontend:latest \
  $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms-frontend:latest

# 6. Update ECS service
aws ecs update-service \
  --cluster ai-voice-sms-dev \
  --service ai-voice-sms-api \
  --force-new-deployment

# 7. Wait for deployment
aws ecs wait services-stable \
  --cluster ai-voice-sms-dev \
  --services ai-voice-sms-api
```

### Step 7: Verify Deployment (10 min)

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Test health endpoint
curl http://$ALB_DNS/health

# Test signup endpoint
curl -X POST http://$ALB_DNS/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "business_type": "hvac_contractor"
  }'

# Check API docs
curl http://$ALB_DNS/docs
```

### Step 8: Run Load Tests (10 min)

```bash
# Install k6 (if not already installed)
brew install k6

# Run load tests against dev environment
API_URL="http://$ALB_DNS" k6 run tests/load/api_load.js
```

### Step 9: Setup Monitoring (15 min)

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name ai-voice-sms-dev-high-cpu \
  --alarm-actions arn:aws:sns:us-east-1:$ACCOUNT_ID:alerts \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Create SNS topic for alerts
aws sns create-topic --name ai-voice-sms-alerts

# Subscribe to alerts (replace with your email)
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:$ACCOUNT_ID:ai-voice-sms-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

---

## 📊 Deployment Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | AWS Setup | 30 min | ⏳ |
| 2 | GitHub Secrets | 10 min | ⏳ |
| 3 | Terraform Init | 10 min | ⏳ |
| 4 | Deploy Infra | 20 min | ⏳ |
| 5 | Run Tests | 15 min | ⏳ |
| 6 | Deploy App | 20 min | ⏳ |
| 7 | Verify | 10 min | ⏳ |
| 8 | Load Test | 10 min | ⏳ |
| 9 | Monitoring | 15 min | ⏳ |
| **TOTAL** | **Dev Environment Live** | **~2 hours** | 🚀 |

---

## ✅ Success Criteria

After following all steps, you should have:

- [ ] AWS infrastructure deployed (VPC, RDS, ElastiCache, ECS)
- [ ] Backend API accessible at `http://$ALB_DNS`
- [ ] Frontend accessible at `http://$ALB_DNS/frontend` (or separate S3 URL)
- [ ] Database migrations successful
- [ ] Health check returning 200
- [ ] Signup endpoint working
- [ ] Load tests passing (error rate < 10%)
- [ ] CloudWatch logs streaming
- [ ] Alarms configured
- [ ] Monthly cost < $50 (dev environment)

---

## 🔍 Troubleshooting

### Terraform Apply Fails
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket exists
aws s3 ls | grep terraform-state

# Check DynamoDB table
aws dynamodb describe-table --table-name terraform-locks
```

### ECS Service Fails to Start
```bash
# Check logs
aws logs tail /ecs/ai-voice-sms-dev --follow

# Check task definition
aws ecs describe-task-definition --task-definition ai-voice-sms-api

# Check service status
aws ecs describe-services --cluster ai-voice-sms-dev --services ai-voice-sms-api
```

### Health Check Failing
```bash
# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <from outputs>

# Check security groups allow port 8000
aws ec2 describe-security-groups --group-ids <api-sg-id>

# SSH into EC2 and check app
# curl localhost:8000/health
```

### Database Connection Error
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier ai-voice-sms-dev

# Test connection from EC2
# psql -h <rds-endpoint> -U admin -d aivoicesms_dev
```

---

## 🛑 Rollback Procedure

If something goes wrong:

```bash
# Rollback to previous ECS version
aws ecs update-service \
  --cluster ai-voice-sms-dev \
  --service ai-voice-sms-api \
  --task-definition ai-voice-sms-api:PREVIOUS_VERSION

# Rollback Terraform
terraform destroy -var-file="environments/dev-ultra-optimized.tfvars"

# Or revert to previous state
# terraform apply -var-file="environments/dev-ultra-optimized.tfvars" -auto-approve
```

---

## 💰 Monthly Cost

**Dev Environment:**
- EC2: ~$5
- RDS: ~$15
- ElastiCache: ~$10
- Data Transfer: ~$2
- **Total: ~$32/month**

---

## 📝 Next Steps After Deployment

1. **Week 2:** Run smoke tests, verify monitoring
2. **Week 3:** Deploy staging environment  
3. **Week 4:** Implement Phase 11 (Calendar Integration)
4. **Week 8:** Add CRM integrations (ServiceTitan, Jobber)
5. **Week 16:** Beta launch to users

---

## 📞 Support

- **Deployment fails?** → Check DEPLOYMENT_CHECKLIST.md
- **Need rollback?** → See Rollback Procedure above
- **Cost concerns?** → See COST_OPTIMIZATION_STRATEGY.md
- **Architecture questions?** → See ARCHITECTURE_DIAGRAMS.md

---

**Status:** 🟢 Ready for Deployment
**Last Updated:** 2026-08-23
**Deployment Time:** ~2 hours
**Team:** DevOps / Backend engineers

Ready to start? Execute Step 1 above! 🚀
