# Terraform Infrastructure - Multi-Cloud Support

This directory contains Terraform configurations for deploying the AI Voice & SMS Platform to different cloud providers.

---

## Directory Structure

```
infrastructure/terraform/
├── aws/                          # ⭐ RECOMMENDED - AWS Terraform
│   ├── main.tf                   # Main configuration
│   ├── variables.tf              # Variable definitions
│   ├── environments/             # Environment-specific settings
│   │   ├── dev.tfvars           # Development ($88/month)
│   │   ├── staging.tfvars       # Staging ($314/month)
│   │   └── production.tfvars    # Production ($2,400/month)
│   ├── modules/                  # Terraform modules
│   │   ├── vpc/                 # VPC, subnets, networking
│   │   ├── security_groups/     # Security group rules
│   │   ├── rds/                 # PostgreSQL database
│   │   ├── elasticache/         # Redis cache
│   │   ├── ecs/                 # Container orchestration
│   │   ├── alb/                 # Load balancer
│   │   ├── s3/                  # Object storage
│   │   ├── cloudfront/          # CDN
│   │   └── monitoring/          # CloudWatch monitoring
│   ├── TERRAFORM_DEPLOYMENT_GUIDE.md  # Deployment guide (2000+ lines)
│   └── COST_OPTIMIZATION.md     # Cost savings strategies (1500+ lines)
│
└── gcp/                          # GCP Terraform (Alternative)
    ├── main.tf                   # Main configuration
    ├── provider.tf               # GCP provider setup
    ├── variables.tf              # Variable definitions
    ├── cloud_run.tf              # Cloud Run container service
    ├── gke-cluster.tf            # Kubernetes cluster
    ├── outputs.tf                # Output values
    ├── locals.tf                 # Local variables
    ├── backend.tf                # State backend
    ├── README.md                 # GCP deployment guide
    └── DEPLOYMENT_GUIDE.md       # GCP-specific instructions
```

---

## Cloud Provider Comparison

### **AWS (⭐ RECOMMENDED)**

**Best For:** This project (Twilio integration, cost optimization)

**Pros:**
- ✅ 25-50% cheaper than GCP
- ✅ Better Twilio integration
- ✅ More cost optimization options
- ✅ Fargate Spot instances (70% savings)
- ✅ DynamoDB for conversation state
- ✅ EventBridge for event routing

**Monthly Cost:**
- Dev: $88
- Staging: $314
- Prod: $2,400 (optimized)

**Get Started:**
```bash
cd aws/
terraform init
terraform apply -var-file="environments/dev.tfvars"
```

See: [aws/TERRAFORM_DEPLOYMENT_GUIDE.md](aws/TERRAFORM_DEPLOYMENT_GUIDE.md)

---

### **GCP (Alternative)**

**Best For:** If you prefer Google Cloud or use Gemini API heavily

**Pros:**
- ✅ Simpler pricing model
- ✅ Better Vertex AI integration
- ✅ Excellent documentation
- ✅ Generous free tier ($300 credit)
- ✅ BigQuery for analytics

**Monthly Cost:**
- Dev: $150
- Staging: $600
- Prod: $3,500+

**Get Started:**
```bash
cd gcp/
terraform init
terraform apply
```

See: [gcp/DEPLOYMENT_GUIDE.md](gcp/DEPLOYMENT_GUIDE.md)

---

## Quick Start

### Option 1: Deploy to AWS (Recommended)

```bash
# Navigate to AWS terraform
cd aws/

# Initialize
terraform init

# Plan deployment
terraform plan -var-file="environments/dev.tfvars"

# Apply configuration
terraform apply -var-file="environments/dev.tfvars"
```

### Option 2: Deploy to GCP

```bash
# Navigate to GCP terraform
cd gcp/

# Initialize
terraform init

# Apply configuration
terraform apply
```

---

## Cost Comparison

| Aspect | AWS | GCP |
|--------|-----|-----|
| **Dev/month** | $88 | $150 |
| **Staging/month** | $314 | $600 |
| **Prod/month** | $2,400 | $3,500+ |
| **Year 1** | $32,424 | $49,800+ |
| **With RI (-30%)** | $22,704 | No RI available |
| **Savings** | ✅ Best | ❌ Higher |
| **Twilio** | ✅ Better | OK |
| **LLM** | ✅✅ OpenAI friendly | ✅✅✅ Gemini native |

**Recommendation: AWS saves ~$17,000/year**

---

## Deployment Guide

### AWS (Recommended Path)

1. **Prerequisites**
   - Install: Terraform, AWS CLI
   - Configure: AWS credentials
   - Time: 30 minutes

2. **Deploy Development** (~$88/month)
   - Start small to test setup
   - Use Spot instances (70% cheaper)
   - Skip backups and monitoring

3. **Deploy Staging** (~$314/month)
   - Mix of Spot + On-Demand
   - Add monitoring
   - Weekly backups

4. **Deploy Production** (~$2,400/month optimized)
   - HA across 3 AZs
   - Multi-AZ database
   - Reserved Instances (-30%)
   - Comprehensive monitoring

### GCP Alternative Path

1. **Prerequisites**
   - Install: Terraform, gcloud CLI
   - Configure: GCP project and credentials
   - Time: 20 minutes

2. **Deploy to Cloud Run**
   - Simpler than AWS
   - Auto-scaling included
   - Good for smaller workloads

3. **Optional: Add GKE**
   - Kubernetes cluster
   - For advanced use cases

---

## Cost Optimization Features

### AWS Optimizations (Included)
- ✅ Fargate Spot (save 70%)
- ✅ Reserved Instances (save 30-47%)
- ✅ Right-sized instances
- ✅ Single NAT Gateway
- ✅ S3 Lifecycle policies
- ✅ CloudFront tiering
- ✅ Log retention limits
- ✅ Auto-scaling policies

### Potential Savings
```
Without optimization:  $3,463/month
With optimization:     $2,400/month (-31%)
With Reserved RI:      $1,680/month (-51%)
With full optimization: $1,500/month (-57%)

Year 1 savings: $23,232 - $26,148
```

---

## Documentation

### AWS
- **[TERRAFORM_DEPLOYMENT_GUIDE.md](aws/TERRAFORM_DEPLOYMENT_GUIDE.md)** - 2000+ line step-by-step guide
- **[COST_OPTIMIZATION.md](aws/COST_OPTIMIZATION.md)** - 1500+ line savings strategies
- **[main.tf](aws/main.tf)** - Main configuration (300 lines)
- **[environments/](aws/environments/)** - Dev, staging, production configs

### GCP
- **[DEPLOYMENT_GUIDE.md](gcp/DEPLOYMENT_GUIDE.md)** - GCP-specific guide
- **[README.md](gcp/README.md)** - Quick reference
- **[main.tf](gcp/main.tf)** - GCP configuration

---

## Environment Variables

### AWS Required
```bash
# Before deploying to production
export AWS_REGION="us-east-1"
export TF_VAR_db_password="YourSecurePassword123!"

# Verify
aws sts get-caller-identity
```

### GCP Required
```bash
# Before deploying
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Verify
gcloud auth list
gcloud config get-value project
```

---

## State Management

### AWS (Recommended)
```bash
# Create S3 backend for state
aws s3 mb s3://ai-voice-sms-terraform-state

# Create DynamoDB for locks
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Configure in main.tf
# Uncomment backend block
```

### GCP
```bash
# Create Cloud Storage bucket
gsutil mb gs://ai-voice-sms-terraform-state

# Configure in backend.tf
# Update bucket name
```

---

## Monitoring & Alerts

### AWS CloudWatch
```bash
# View costs
aws ce get-cost-and-usage \
  --time-period Start=2025-08-01,End=2025-08-31 \
  --granularity MONTHLY \
  --metrics UnblendedCost

# Create alert
aws cloudwatch put-metric-alarm \
  --alarm-name HighAWSCosts \
  --threshold 3000 \
  --comparison-operator GreaterThanThreshold
```

### GCP Cloud Monitoring
```bash
# View costs in Cloud Console
# https://console.cloud.google.com/billing

# Create alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget" \
  --budget-amount=3000
```

---

## Troubleshooting

### Common Issues

**AWS: "error getting credentials"**
```bash
aws configure
aws sts get-caller-identity
```

**GCP: "Invalid credentials"**
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Terraform: "module not found"**
```bash
# Reinitialize
terraform init -upgrade
terraform get -update
```

---

## Next Steps

1. **Choose Cloud Provider**
   - AWS (recommended) or GCP?

2. **Read Deployment Guide**
   - `aws/TERRAFORM_DEPLOYMENT_GUIDE.md` or `gcp/DEPLOYMENT_GUIDE.md`

3. **Deploy Development**
   - Test infrastructure setup
   - Verify scaling works
   - Monitor costs

4. **Deploy Staging** (Optional)
   - Test with realistic load
   - Verify backups/failover
   - Test monitoring

5. **Deploy Production**
   - Full HA setup
   - Purchase Reserved Instances (AWS)
   - Enable monitoring/alarms
   - Setup cost controls

---

## Support

- **AWS Help:** See [aws/TERRAFORM_DEPLOYMENT_GUIDE.md](aws/TERRAFORM_DEPLOYMENT_GUIDE.md) > Troubleshooting
- **GCP Help:** See [gcp/DEPLOYMENT_GUIDE.md](gcp/DEPLOYMENT_GUIDE.md)
- **Terraform Docs:** https://www.terraform.io/docs
- **AWS Docs:** https://docs.aws.amazon.com
- **GCP Docs:** https://cloud.google.com/docs

---

## Recommendation

### For Production:
**Use AWS** - Save 30-50% on infrastructure costs with optimizations built-in.

### For Gemini-Heavy Workloads:
**Use GCP** - Native Vertex AI integration and BigQuery analytics.

### For Maximum Flexibility:
**Deploy to Both** - Mirror critical services across both clouds for redundancy.

---

**Last Updated:** August 2026  
**Terraform Version:** 1.0+  
**Status:** Production Ready ✅
