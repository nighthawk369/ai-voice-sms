# Terraform Deployment Guide - AWS Infrastructure
## AI Voice & SMS Platform - Cost Optimized

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Cost Optimization Strategies](#cost-optimization-strategies)
4. [Deployment Instructions](#deployment-instructions)
5. [Cost Monitoring](#cost-monitoring)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
```bash
# Install Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# Verify installation
terraform --version

# Install AWS CLI
brew install awscli
aws --version

# Install jq (optional, for JSON processing)
brew install jq
```

### AWS Account Setup
```bash
# Configure AWS credentials
aws configure

# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
# Default output format: json

# Verify AWS credentials
aws sts get-caller-identity
```

### AWS IAM Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "rds:*",
        "elasticache:*",
        "ecs:*",
        "ecr:*",
        "elasticloadbalancing:*",
        "s3:*",
        "cloudfront:*",
        "cloudwatch:*",
        "logs:*",
        "iam:*",
        "sns:*",
        "sqs:*",
        "secretsmanager:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Project Structure

```
terraform/
├── main.tf                           # Main Terraform configuration
├── variables.tf                      # Variable definitions
├── environments/
│   ├── dev.tfvars                   # Development environment (cost optimized)
│   ├── staging.tfvars               # Staging environment (balanced)
│   └── production.tfvars            # Production environment (HA)
├── modules/
│   ├── vpc/                         # VPC + Subnets + NAT
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── security_groups/             # ALB, ECS, RDS, ElastiCache SGs
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/                         # RDS PostgreSQL
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── elasticache/                 # Redis cache
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/                         # ECS cluster + service
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── alb/                         # Application Load Balancer
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── s3/                          # S3 buckets + lifecycle policies
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloudfront/                  # CloudFront CDN
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/                  # CloudWatch + Alarms
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── TERRAFORM_DEPLOYMENT_GUIDE.md    # This file
```

---

## Cost Optimization Strategies

### 1. **Development Environment** (~$88/month)

#### Enabled Optimizations:
- ✅ Single AZ (not multi-AZ)
- ✅ Micro instances (0.25 vCPU, 512 MB RAM)
- ✅ 100% Fargate Spot instances (70% cheaper)
- ✅ No database backups
- ✅ No monitoring/Performance Insights
- ✅ 1-day log retention
- ✅ No S3 versioning
- ✅ Cheapest CloudFront price class

#### Cost Breakdown:
```
ECS Fargate Spot (0.25vCPU):  $5/month
RDS t3.micro:                $31/month
ElastiCache t3.micro:        $16/month
ALB:                         $16/month
S3 + CloudFront:             $1/month
CloudWatch:                  $10/month
Other:                       $10/month
─────────────────────────────────────
TOTAL:                       $89/month
```

**Deploy Command:**
```bash
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

---

### 2. **Staging Environment** (~$314/month)

#### Enabled Optimizations:
- ✅ 2 AZ (some resilience)
- ✅ Small instances (0.5 vCPU, 1 GB RAM)
- ✅ 70% Fargate Spot + 30% On-Demand
- ✅ Weekly backups
- ✅ Container Insights enabled
- ✅ 7-day log retention
- ✅ S3 versioning with lifecycle policies

#### Cost Breakdown:
```
ECS Fargate (mixed):         $65/month
RDS t3.small:               $62/month
ElastiCache t3.small:       $32/month
NAT Gateway:                $32/month
ALB:                        $16/month
S3 + CloudFront:            $2/month
CloudWatch:                 $15/month
Container Insights:         $15/month
Other:                      $75/month
─────────────────────────────────────
TOTAL:                      $314/month
```

**Deploy Command:**
```bash
terraform init
terraform plan -var-file="environments/staging.tfvars"
terraform apply -var-file="environments/staging.tfvars"
```

---

### 3. **Production Environment** (~$2,400-2,800/month with optimization)

#### High Availability Features:
- ✅ 3 AZ (full redundancy)
- ✅ RDS Multi-AZ (automatic failover)
- ✅ ElastiCache Multi-AZ (automatic failover)
- ✅ Auto-scaling (1-10 instances)
- ✅ 30-day backups
- ✅ Performance Insights enabled
- ✅ 30-day log retention
- ✅ Global CloudFront distribution

#### Cost Savings Opportunities:
```
BASE COST (On-Demand):         $3,463/month

Cost Reductions:
├─ RDS 1-year Reserved (-30%): -$75/month
├─ ElastiCache Reserved (-30%):  -$39/month
├─ CloudFront optimization:     -$50/month
├─ S3 Intelligent-Tiering:      -$200/month
├─ Auto-scaling (night):        -$300/month
└─ Spot instances (optional):   -$400/month

OPTIMIZED COST:                ~$2,400/month
```

#### Reserved Instances Calculation:
```
RDS db.t3.medium:
- On-Demand: $251/month = $3,012/year
- 1-Year Reserved: $2,111/year (-30%) = Save $901/year
- 3-Year Reserved: $1,587/year (-47%) = Save $1,425/year

ElastiCache r6g.large:
- On-Demand: $130/month = $1,560/year
- 1-Year Reserved: $1,092/year (-30%) = Save $468/year
- 3-Year Reserved: $819/year (-47%) = Save $741/year

Total Year 1 Savings: $1,369 (with 1-year reserved)
Total Year 3 Savings: $2,166 (with 3-year reserved)
```

**Deploy Command:**
```bash
# First, create the infrastructure
terraform init
terraform plan -var-file="environments/production.tfvars"

# Review the plan carefully
terraform apply -var-file="environments/production.tfvars"

# After deployment, purchase Reserved Instances in AWS console
# This will further reduce costs by 30-47%
```

---

## Deployment Instructions

### Step 1: Initialize Terraform
```bash
cd terraform/

# Initialize Terraform (downloads providers)
terraform init

# Verify modules are recognized
terraform get
```

### Step 2: Create Backend for State (Optional but Recommended)
```bash
# Create S3 bucket for state
aws s3 mb s3://ai-voice-sms-terraform-state-$(date +%s)

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Update main.tf with your state bucket name
# Uncomment the backend block in main.tf
```

### Step 3: Plan Deployment
```bash
# For Development
terraform plan -var-file="environments/dev.tfvars" -out=tfplan-dev

# Review the plan (shows all resources to be created)
terraform show tfplan-dev

# For Staging (if deploying)
terraform plan -var-file="environments/staging.tfvars" -out=tfplan-staging

# For Production (be very careful!)
terraform plan -var-file="environments/production.tfvars" -out=tfplan-prod
```

### Step 4: Apply Configuration
```bash
# Development deployment
terraform apply tfplan-dev

# Staging deployment
terraform apply tfplan-staging

# Production deployment (requires manual approval)
terraform apply tfplan-prod

# Or without pre-planning:
terraform apply -var-file="environments/dev.tfvars" -auto-approve
```

### Step 5: Retrieve Outputs
```bash
# Show all outputs
terraform output

# Get specific values
terraform output -json > outputs.json

# Show RDS endpoint
terraform output rds_endpoint

# Show load balancer DNS
terraform output alb_dns_name
```

### Step 6: Deploy Docker Image to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name ai-voice-sms --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t ai-voice-sms:latest .
docker tag ai-voice-sms:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ai-voice-sms:latest

# Update ECS service with new image
aws ecs update-service \
  --cluster ai-voice-sms-dev-cluster \
  --service ai-voice-sms-api \
  --force-new-deployment
```

---

## Cost Monitoring

### 1. AWS Cost Explorer
```bash
# Open AWS Cost Explorer in console
# https://console.aws.amazon.com/cost-management/home

# Create custom reports by:
- Service (ECS, RDS, ElastiCache, ALB, etc.)
- Environment (dev, staging, prod)
- Cost Center
- Time period
```

### 2. CloudWatch Alarms (Cost-Based)
```bash
# Create alarm if monthly bill exceeds threshold
aws cloudwatch put-metric-alarm \
  --alarm-name EstimatedCharges \
  --alarm-description "Alert if estimated charges exceed $100" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 100 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:your-sns-topic
```

### 3. Tagging Strategy for Cost Allocation
```bash
# All resources have tags:
- Environment: dev, staging, production
- Project: ai-voice-sms
- ManagedBy: Terraform
- CostCenter: engineering

# View costs by tag in AWS Cost Explorer
```

### 4. Cost Anomaly Detection
```bash
# Enable in AWS Cost Management console
# Will alert if spending is abnormal for this account
```

---

## Troubleshooting

### Common Issues

#### 1. "Error: error getting credentials"
```bash
# Solution: Configure AWS credentials
aws configure
aws sts get-caller-identity  # Verify

# Or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

#### 2. "Error: Provider version constraint incompatible"
```bash
# Solution: Update Terraform
terraform version
brew upgrade terraform

# Or lock to specific version
terraform init -upgrade
```

#### 3. "Error: error creating DB instance: InvalidParameterValue"
```bash
# Solution: Verify DB password meets requirements
# - At least 8 characters
# - Contains uppercase, lowercase, numbers, special chars
# - Doesn't contain reserved characters

# Set password via environment variable (more secure)
export TF_VAR_db_password="YourSecurePassword123!"
terraform apply
```

#### 4. "Error: VPC has no Internet Gateway"
```bash
# Solution: Ensure enable_nat_gateway = true in tfvars
# Or check that internet gateway was created
aws ec2 describe-internet-gateways
```

#### 5. "Error: Target group not found for ALB"
```bash
# Solution: Check that ALB module deployed successfully
terraform state list | grep alb
terraform state show 'module.alb'
```

### Useful Debugging Commands

```bash
# Show Terraform state
terraform state list
terraform state show 'module.rds'

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Check for drift
terraform plan | grep -i "no changes"

# Destroy specific resource (be careful!)
terraform destroy -target='module.rds.aws_db_instance.main'

# View all resources in state
terraform state list

# View specific resource details
terraform state show 'aws_vpc.main'
```

---

## Next Steps

### After Successful Deployment:

1. **Set Database Password in Secrets Manager**
   ```bash
   aws secretsmanager create-secret \
     --name ai-voice-sms/prod/db_password \
     --secret-string "YourSecurePassword"
   ```

2. **Configure Monitoring Dashboards**
   ```bash
   aws cloudwatch put-dashboard \
     --dashboard-name ai-voice-sms-prod \
     --dashboard-body file://dashboards/prod.json
   ```

3. **Setup Auto-Scaling Policies**
   ```bash
   # Terraform includes these, but verify:
   aws application-autoscaling describe-scalable-targets \
     --service-namespace ecs
   ```

4. **Purchase Reserved Instances** (Save 30-47%)
   ```bash
   # Go to AWS console:
   # EC2 > Reserved Instances > Purchase Reserved Instances
   # Select 1-year or 3-year terms for RDS + ElastiCache
   ```

5. **Enable Cost Anomaly Detection**
   ```bash
   # AWS Console > Cost Management > Anomaly Detector
   # Set threshold and SNS topic for alerts
   ```

6. **Create CloudWatch Dashboard**
   ```bash
   # See outputs for ALB DNS, RDS endpoint, etc.
   terraform output -json > infrastructure.json
   # Use these values in CloudWatch dashboards
   ```

---

## Cost Comparison Summary

| Environment | Monthly Cost | Annual Cost | Per Call (10K) |
|-------------|-------------|------------|--------|
| Dev (optimized) | $88 | $1,056 | N/A |
| Staging (optimized) | $314 | $3,776 | N/A |
| Prod (no optimization) | $3,463 | $41,556 | $0.35 |
| Prod (with reserved) | $2,400 | $28,800 | $0.24 |
| Prod (full optimization) | $2,100 | $25,200 | $0.21 |

---

## Support & Questions

For issues:
1. Check [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
2. Review AWS CloudFormation Events for deployment errors
3. Check CloudWatch Logs for application errors
4. Review AWS Support Plan

---

**Last Updated:** August 2026
**Terraform Version:** 1.0+
**AWS Provider Version:** 5.0+
