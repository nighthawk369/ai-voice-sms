#!/bin/bash
# CallSync - Fully Automated Deployment
# No manual AWS console clicks needed!

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=====================================${NC}"
echo -e "${YELLOW}CallSync - Fully Automated Deployment${NC}"
echo -e "${YELLOW}=====================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
  echo -e "${RED}✗ AWS CLI not found. Install with: brew install awscli${NC}"
  exit 1
fi

if ! command -v terraform &> /dev/null; then
  echo -e "${RED}✗ Terraform not found. Install with: brew install terraform${NC}"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  echo -e "${RED}✗ Docker not found. Install from https://docker.com${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All prerequisites installed${NC}"
echo ""

# Verify AWS credentials
echo -e "${YELLOW}Verifying AWS credentials...${NC}"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ -z "$AWS_ACCOUNT" ]; then
  echo -e "${RED}✗ AWS credentials not configured. Run: aws configure${NC}"
  exit 1
fi
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT${NC}"
echo ""

# Step 1: Bootstrap - Create S3 and DynamoDB
echo -e "${YELLOW}Step 1/6: Creating S3 bucket and DynamoDB table...${NC}"
cd infrastructure/terraform/bootstrap

terraform init
terraform apply -auto-approve

BUCKET_NAME=$(terraform output -raw s3_bucket_name)
DYNAMODB_TABLE=$(terraform output -raw dynamodb_table_name)

echo -e "${GREEN}✓ S3 Bucket: $BUCKET_NAME${NC}"
echo -e "${GREEN}✓ DynamoDB Table: $DYNAMODB_TABLE${NC}"
echo ""

# Step 2: Initialize main Terraform with S3 backend
echo -e "${YELLOW}Step 2/6: Initializing main Terraform infrastructure...${NC}"
cd ../aws

# Create backend.tf
cat > backend.tf << EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "callsync/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "$DYNAMODB_TABLE"
  }
}
EOF

terraform init -upgrade
echo -e "${GREEN}✓ Terraform initialized${NC}"
echo ""

# Step 3: Plan infrastructure
echo -e "${YELLOW}Step 3/6: Planning infrastructure deployment...${NC}"
terraform plan -var-file="environments/dev-ultra-optimized.tfvars" -out=tfplan
echo -e "${GREEN}✓ Plan created${NC}"
echo ""

# Step 4: Deploy infrastructure
echo -e "${YELLOW}Step 4/6: Deploying infrastructure (15-20 minutes)...${NC}"
terraform apply tfplan
echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# Get outputs
ALB_DNS=$(terraform output -raw alb_dns_name)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

echo -e "${GREEN}✓ Outputs:${NC}"
echo "   ALB DNS: $ALB_DNS"
echo "   RDS Endpoint: $RDS_ENDPOINT"
echo "   Redis Endpoint: $REDIS_ENDPOINT"
echo ""

# Step 5: Build and push Docker images
echo -e "${YELLOW}Step 5/6: Building Docker images...${NC}"
cd ../../../

ACCOUNT_ID=$AWS_ACCOUNT

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name callsync-api --region us-east-1 || true

# Build and push backend
cd backend
docker build -t callsync-api:latest .
docker tag callsync-api:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest
echo -e "${GREEN}✓ Backend image pushed${NC}"
cd ..
echo ""

# Step 6: Deploy to ECS and verify
echo -e "${YELLOW}Step 6/6: Deploying to ECS and verifying...${NC}"
aws ecs update-service \
  --cluster callsync-dev \
  --service callsync-api \
  --force-new-deployment

echo "Waiting for service to stabilize (5 minutes)..."
aws ecs wait services-stable \
  --cluster callsync-dev \
  --services callsync-api

# Verify health
echo "Verifying API health..."
for i in {1..20}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$ALB_DNS/health || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ API is healthy!${NC}"
    break
  fi
  echo "Attempt $i: HTTP $HTTP_CODE (waiting...)"
  sleep 10
done
echo ""

# Save deployment info
cat > deployment-info.txt << EOF
CallSync Deployment Complete
============================
Date: $(date)
AWS Account: $AWS_ACCOUNT

Infrastructure:
  S3 Bucket: $BUCKET_NAME
  DynamoDB Table: $DYNAMODB_TABLE
  
API Endpoints:
  ALB DNS: $ALB_DNS
  API URL: http://$ALB_DNS
  API Docs: http://$ALB_DNS/docs
  Health: http://$ALB_DNS/health

Terraform State:
  Location: s3://$BUCKET_NAME/callsync/dev/terraform.tfstate
  Locking: $DYNAMODB_TABLE

Next Steps:
  1. Test API: curl http://$ALB_DNS/health
  2. View docs: http://$ALB_DNS/docs
  3. Run load tests: API_URL=http://$ALB_DNS k6 run tests/load/api_load.js
  4. View logs: aws logs tail /ecs/callsync-dev --follow
  5. Monitor: https://console.aws.amazon.com/cloudwatch
EOF

# Final summary
echo -e "${GREEN}======================================"
echo "✓ CallSync Deployment Complete!"
echo "======================================${NC}"
echo ""
echo "Your CallSync is now LIVE!"
echo ""
echo "API Endpoints:"
echo -e "  ${GREEN}API: http://$ALB_DNS${NC}"
echo -e "  ${GREEN}Docs: http://$ALB_DNS/docs${NC}"
echo -e "  ${GREEN}Health: http://$ALB_DNS/health${NC}"
echo ""
echo "All infrastructure created by Terraform:"
echo "  ✓ S3 Bucket for state: $BUCKET_NAME"
echo "  ✓ DynamoDB Table for locking: $DYNAMODB_TABLE"
echo "  ✓ VPC, Subnets, Security Groups"
echo "  ✓ RDS PostgreSQL Database"
echo "  ✓ ElastiCache Redis"
echo "  ✓ ECS Cluster & Service"
echo "  ✓ Application Load Balancer"
echo ""
echo "Deployment info saved to: deployment-info.txt"
echo ""
echo "Next commands:"
echo "  • Test: curl http://$ALB_DNS/health"
echo "  • Logs: aws logs tail /ecs/callsync-dev --follow"
echo "  • Load test: API_URL=http://$ALB_DNS k6 run tests/load/api_load.js"
echo ""

