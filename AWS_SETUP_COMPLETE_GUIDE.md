# AWS Setup Complete Guide - UI Navigation Step by Step

## Phase 1: Create AWS Account (Skip if you have one)

### Step 1.1: Create AWS Account

1. Go to https://aws.amazon.com
2. Click "Create an AWS Account" (top right)
3. Enter:
   - Email address: your-email@example.com
   - AWS account name: callsync-dev
   - Password: Strong password (8+ chars)
4. Click "Verify email address"
5. Go to your email inbox and verify
6. Select "Personal" for account type
7. Enter contact information
8. Add payment method (charged $1, refunded)
9. Verify identity via SMS/Phone
10. Select "Basic support" (free)

**You now have an AWS account!**

---

## Phase 2: Create IAM User & Access Keys

### Step 2.1: Sign In to AWS Console

1. Go to https://console.aws.amazon.com
2. Sign in with your email and password
3. You're in the AWS Management Console

### Step 2.2: Navigate to IAM

1. Search for "IAM" in the search bar (top)
2. Click "IAM" from results
3. You're in IAM Dashboard

### Step 2.3: Create IAM User

1. Left sidebar: Click "Users"
2. Click "Create user" (orange button, top right)
3. Enter: User name = "callsync-dev-user"
4. Click "Next"
5. Choose "Attach policies directly"
6. Search for "AdministratorAccess"
7. Check the box for AdministratorAccess
8. Click "Next"
9. Click "Create user"

**IAM user created!**

### Step 2.4: Create Access Key & Secret

1. Click "Users" (left sidebar)
2. Click "callsync-dev-user"
3. Scroll to "Access keys" section
4. Click "Create access key"
5. Select: Use case = "Command Line Interface (CLI)"
6. Check: "I understand..."
7. Click "Next"
8. Description: "CallSync Terraform Deployment"
9. Click "Create access key"

**SAVE THESE IMMEDIATELY:**
- Access Key ID: AKIA...
- Secret Access Key: wJal...

Click "Done"

---

## Phase 3: Configure AWS CLI Locally

### Step 3.1: Install AWS CLI

Mac:
```
brew install awscli
```

Verify:
```
aws --version
```

### Step 3.2: Configure Credentials

```
aws configure
```

Enter when prompted:
- AWS Access Key ID: (paste your AKIA...)
- AWS Secret Access Key: (paste your wJal...)
- Default region name: us-east-1
- Default output format: json

### Step 3.3: Verify

```
aws sts get-caller-identity
```

Should show your AWS account info.

---

## Phase 4: Create S3 Bucket for Terraform

### Step 4.1: Navigate to S3

1. Go to https://console.aws.amazon.com
2. Search for "S3"
3. Click "S3"
4. You're in S3 Dashboard

### Step 4.2: Create Bucket

1. Click "Create bucket" (orange button)
2. Bucket name: callsync-terraform-state-nikhil
   (Replace "nikhil" with your name - must be globally unique)
3. Region: us-east-1
4. Keep "Block all public access" checked
5. Click "Create bucket"

**S3 bucket created!**

### Step 4.3: Save Bucket Name

```
BUCKET_NAME="callsync-terraform-state-nikhil"
```

---

## Phase 5: Create DynamoDB Table

### Step 5.1: Navigate to DynamoDB

1. Go to https://console.aws.amazon.com
2. Search for "DynamoDB"
3. Click "DynamoDB"
4. You're in DynamoDB Dashboard

### Step 5.2: Create Table

1. Click "Create table"
2. Table name: terraform-locks
3. Partition key: LockID (String)
4. Click "Create table"
5. Wait 1 minute for creation

**DynamoDB table created!**

---

## Phase 6: Verify Everything

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Verify S3 bucket
aws s3 ls | grep terraform

# Verify DynamoDB table
aws dynamodb describe-table --table-name terraform-locks

echo "All AWS setup complete!"
```

---

## Phase 7: Initialize Terraform

```bash
cd infrastructure/terraform/aws

# Create backend.tf with YOUR bucket name
cat > backend.tf << 'BACKEND'
terraform {
  backend "s3" {
    bucket         = "callsync-terraform-state-nikhil"
    key            = "callsync/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}
BACKEND

# Initialize Terraform
terraform init

# Should say: "Successfully configured the backend"
```

---

## Checklist - AWS Setup Complete

- [ ] AWS account created
- [ ] IAM user created
- [ ] Access Key & Secret created
- [ ] AWS CLI installed
- [ ] AWS credentials configured (aws configure)
- [ ] S3 bucket created
- [ ] DynamoDB table created
- [ ] Terraform initialized

All done? Continue to deployment! 

---

## Next: Run These Deployment Commands

Once AWS setup is complete, run:

```bash
# Step 1: Preview infrastructure
terraform plan -var-file="environments/dev-ultra-optimized.tfvars" -out=tfplan

# Step 2: Deploy infrastructure
terraform apply tfplan

# Step 3: Get outputs
terraform output -json > outputs.json
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "Your ALB: $ALB_DNS"

# Step 4: Build Docker images
cd ../../..
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name callsync-api --region us-east-1 || true

# Build and push backend
cd backend
docker build -t callsync-api:latest .
docker tag callsync-api:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest

# Step 5: Deploy to ECS
aws ecs update-service --cluster callsync-dev --service callsync-api --force-new-deployment

# Step 6: Verify deployment
curl http://$ALB_DNS/health

# Done!
```
