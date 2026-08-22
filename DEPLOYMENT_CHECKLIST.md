# 🚀 Deployment Checklist & Guide

## Pre-Deployment Requirements

### Local Environment Setup
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 15+ installed or Docker available
- [ ] AWS CLI installed and configured
- [ ] Terraform 1.6+ installed
- [ ] Git configured with SSH keys

### AWS Account Setup
- [ ] AWS account created
- [ ] IAM user created with programmatic access
- [ ] AWS credentials configured locally: `aws configure`
- [ ] S3 bucket created for Terraform state
- [ ] CloudWatch Log Group created

### GitHub Setup
- [ ] Repository pushed to GitHub
- [ ] GitHub Actions enabled
- [ ] GitHub Secrets configured:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`

### Environment Files
- [ ] `backend/.env` created (copy from .env.example)
- [ ] `frontend/.env.local` created
- [ ] `mobile/.env` created

---

## Phase 1: Local Testing (Week 1)

### Backend Testing
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-optimized.txt

# Setup test database
export DATABASE_URL="postgresql://user:password@localhost/aivoicesms_test"
alembic upgrade head

# Run tests
python -m pytest tests/test_integration.py -v
```

**Checklist:**
- [ ] All backend tests pass
- [ ] API endpoints accessible at http://localhost:8000
- [ ] /docs endpoint working
- [ ] Database migrations successful

### Frontend Testing
```bash
cd frontend
npm install
npm run build
```

**Checklist:**
- [ ] Build succeeds without errors
- [ ] No TypeScript errors
- [ ] All dependencies resolve

### Mobile Testing
```bash
cd mobile
npm install
npx expo start
```

**Checklist:**
- [ ] App starts in Expo
- [ ] Can connect to backend API
- [ ] Navigation works

---

## Phase 2: AWS Deployment (Week 2)

### Terraform Initialization
```bash
cd infrastructure/terraform/aws

# Initialize with S3 backend
terraform init -backend-config="bucket=your-terraform-state-bucket"

# Validate configuration
terraform validate
```

**Checklist:**
- [ ] Terraform initialized successfully
- [ ] No validation errors

### Deploy Dev Environment
```bash
# Plan deployment
terraform plan -var-file="environments/dev-ultra-optimized.tfvars" -out=tfplan

# Review output
cat tfplan

# Apply
terraform apply tfplan
```

**Checklist:**
- [ ] All resources created:
  - [ ] VPC with subnets
  - [ ] RDS database
  - [ ] ElastiCache Redis
  - [ ] ECS cluster
  - [ ] ALB
  - [ ] Security groups
- [ ] No errors during apply

### Post-Deployment Verification
```bash
# Get outputs
terraform output -json > outputs.json

# Check ALB
ALB_DNS=$(terraform output -raw alb_dns_name)
curl http://$ALB_DNS/health
```

**Checklist:**
- [ ] ALB is accessible
- [ ] Health check endpoint returns 200
- [ ] RDS endpoint is accessible from EC2

---

## Phase 3: Application Deployment

### Database Configuration
```bash
# SSH into EC2 or use Systems Manager
# Set up database
export DATABASE_URL="postgresql://user:password@rds-endpoint/aivoicesms_dev"
cd backend
alembic upgrade head
```

**Checklist:**
- [ ] Database migrations successful
- [ ] Tables created in RDS

### Deploy Backend
```bash
# Using ECS / Container Registry
docker build -t ai-voice-sms:latest backend/
docker tag ai-voice-sms:latest {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest
docker push {ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest

# Update ECS service
aws ecs update-service --cluster ai-voice-sms-dev --service ai-voice-sms-api --force-new-deployment
```

**Checklist:**
- [ ] Docker image pushed to ECR
- [ ] ECS service updated
- [ ] Logs available in CloudWatch

### Deploy Frontend
```bash
# Build static files
cd frontend
npm run build

# Upload to S3
aws s3 sync out/ s3://ai-voice-sms-frontend-dev/

# Invalidate CloudFront cache (if using CloudFront)
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Checklist:**
- [ ] Frontend builds successfully
- [ ] Files uploaded to S3
- [ ] CloudFront cache invalidated

---

## Phase 4: Testing & Verification

### Smoke Tests
```bash
# Test basic endpoints
curl -X GET http://$ALB_DNS/health
curl -X POST http://$ALB_DNS/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","business_type":"hvac_contractor"}'
```

**Checklist:**
- [ ] Health endpoint returns 200
- [ ] Signup endpoint accepts requests
- [ ] No 500 errors

### Integration Tests
```bash
export API_URL="http://$ALB_DNS"
cd backend
python -m pytest tests/test_integration.py -v
```

**Checklist:**
- [ ] User signup works
- [ ] Login works
- [ ] Contact creation works
- [ ] Multi-tenancy isolation verified

### Performance Tests
```bash
# Using k6 (install: brew install k6)
k6 run tests/load/api_load.js
```

**Checklist:**
- [ ] API handles 100+ concurrent users
- [ ] Response times < 2 seconds
- [ ] No 500 errors under load

---

## Phase 5: Monitoring & Alerts

### CloudWatch Configuration
```bash
# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name api-high-latency \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:alert-topic \
  --metric-name Latency \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 2000 \
  --comparison-operator GreaterThanThreshold
```

**Checklist:**
- [ ] CPU utilization alarm created
- [ ] Error rate alarm created
- [ ] Latency alarm created
- [ ] SNS topic configured for notifications

### Logs Configuration
```bash
# Verify CloudWatch Logs are active
aws logs describe-log-groups | grep ai-voice-sms
```

**Checklist:**
- [ ] ECS logs streaming to CloudWatch
- [ ] Application logs visible in CloudWatch Logs
- [ ] Log retention set (30 days recommended)

---

## Phase 6: Backup & Disaster Recovery

### RDS Backups
```bash
# Enable automated backups (should be in Terraform)
aws rds modify-db-instance \
  --db-instance-identifier ai-voice-sms-dev \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00"
```

**Checklist:**
- [ ] Automated backups enabled
- [ ] Backup window configured
- [ ] Backup retention period set

### Test Restore
```bash
# Document restore procedure
# (Don't actually restore unless needed)
echo "Restore procedure: Create DB snapshot → Restore from snapshot → Update connection string"
```

**Checklist:**
- [ ] Restore procedure documented
- [ ] Team knows how to restore
- [ ] Recovery Time Objective (RTO) < 1 hour

---

## Phase 7: Security & Compliance

### SSL/TLS Configuration
```bash
# Request ACM certificate (automatic for *.example.com)
aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names "*.example.com" \
  --validation-method DNS
```

**Checklist:**
- [ ] SSL certificate issued
- [ ] ALB using HTTPS
- [ ] HTTP redirects to HTTPS

### Secrets Management
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name ai-voice-sms/dev/openai_api_key \
  --secret-string "sk-..."

aws secretsmanager create-secret \
  --name ai-voice-sms/dev/db_password \
  --secret-string "password123"
```

**Checklist:**
- [ ] All API keys in Secrets Manager
- [ ] Database password rotated
- [ ] IAM role has read access

### Security Group Review
```bash
# Verify security groups
aws ec2 describe-security-groups --filters "Name=group-name,Values=ai-voice-sms-*"
```

**Checklist:**
- [ ] ALB: Port 80 & 443 open to 0.0.0.0
- [ ] API: Only from ALB
- [ ] RDS: Only from API security group
- [ ] Redis: Only from API security group

---

## Phase 8: Documentation & Handoff

### Documentation
- [ ] Deployment guide written
- [ ] Runbooks created for:
  - [ ] Scaling up
  - [ ] Scaling down
  - [ ] Database backup
  - [ ] Incident response
  - [ ] Rollback procedure

### Team Training
- [ ] Backend team trained on deployment
- [ ] DevOps team has access
- [ ] On-call rotation configured
- [ ] Escalation procedures defined

### Cost Monitoring
```bash
# Enable cost alerts
aws budgets create-budget \
  --account-id ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**Checklist:**
- [ ] Monthly budget set ($550 for dev+staging)
- [ ] Alerts configured
- [ ] Cost optimization review scheduled

---

## Rollback Procedure

If deployment fails:

```bash
# 1. Get previous ECS task definition
aws ecs describe-task-definition --task-definition ai-voice-sms-api:PREVIOUS_VERSION

# 2. Revert to previous version
aws ecs update-service \
  --cluster ai-voice-sms-dev \
  --service ai-voice-sms-api \
  --task-definition ai-voice-sms-api:PREVIOUS_VERSION

# 3. Verify health
curl http://$ALB_DNS/health

# 4. Investigate failure
aws logs tail /ecs/ai-voice-sms-dev --follow
```

**Checklist:**
- [ ] Previous version deployed
- [ ] Health checks passing
- [ ] Root cause identified
- [ ] Post-mortem scheduled

---

## Success Criteria

✅ **Deployment Successful When:**
- All smoke tests pass
- Integration tests pass  
- Load tests complete without errors
- Monitoring shows healthy metrics
- Team can access and manage resources
- Documentation is complete
- Backup & restore procedures work
- Cost is within budget

---

## Support & Escalation

**Issue Resolution Path:**
1. Check CloudWatch logs: `aws logs tail /ecs/ai-voice-sms-dev`
2. Check ALB target health: `aws elbv2 describe-target-health`
3. Check RDS status: `aws rds describe-db-instances`
4. Check ECS task status: `aws ecs list-tasks --cluster ai-voice-sms-dev`
5. Consult DEPLOYMENT_TROUBLESHOOTING.md
6. Escalate to senior DevOps engineer

---

**Last Updated:** 2026-08-23
**Deployment Owner:** Your Team
**Emergency Contact:** DevOps On-Call
**Status:** Ready for Dev Environment Deployment ✅
