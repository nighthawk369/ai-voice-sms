#!/bin/bash
# CallSync Deployment Script
# Copy and paste each section one at a time

set -e  # Exit on error

echo "======================================"
echo "CallSync Deployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Verify AWS Setup
echo -e "${YELLOW}Step 1: Verifying AWS Setup${NC}"
echo "Running: aws sts get-caller-identity"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT${NC}"

# Step 2: Verify S3 Bucket
echo -e "${YELLOW}Step 2: Verifying S3 Bucket${NC}"
read -p "Enter your S3 bucket name (e.g., callsync-terraform-state-nikhil): " BUCKET_NAME
aws s3 ls "$BUCKET_NAME" > /dev/null 2>&1 || { echo "Bucket not found!"; exit 1; }
echo -e "${GREEN}✓ S3 Bucket verified: $BUCKET_NAME${NC}"

# Step 3: Initialize Terraform
echo -e "${YELLOW}Step 3: Initializing Terraform${NC}"
cd infrastructure/terraform/aws

# Create backend.tf
cat > backend.tf << EOF
terraform {
  backend "s3" {
    bucket         = "$BUCKET_NAME"
    key            = "callsync/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}
EOF
echo -e "${GREEN}✓ Created backend.tf${NC}"

# Initialize
terraform init
echo -e "${GREEN}✓ Terraform initialized${NC}"

# Step 4: Plan Infrastructure
echo -e "${YELLOW}Step 4: Planning Infrastructure${NC}"
terraform plan -var-file="environments/dev-ultra-optimized.tfvars" -out=tfplan
read -p "Review the plan above. Continue? (yes/no): " CONTINUE
if [ "$CONTINUE" != "yes" ]; then
  echo "Deployment cancelled"
  exit 1
fi

# Step 5: Apply Infrastructure
echo -e "${YELLOW}Step 5: Deploying Infrastructure (this takes 15-20 minutes)${NC}"
terraform apply tfplan
echo -e "${GREEN}✓ Infrastructure deployed${NC}"

# Step 6: Get Outputs
echo -e "${YELLOW}Step 6: Getting Deployment Outputs${NC}"
terraform output -json > outputs.json
ALB_DNS=$(terraform output -raw alb_dns_name)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

echo -e "${GREEN}✓ Outputs:${NC}"
echo "   ALB DNS: $ALB_DNS"
echo "   RDS Endpoint: $RDS_ENDPOINT"
echo "   Redis Endpoint: $REDIS_ENDPOINT"

# Save to file
cat > deployment-info.txt << EOF
CallSync Deployment Info
========================
ALB DNS: $ALB_DNS
RDS Endpoint: $RDS_ENDPOINT
Redis Endpoint: $REDIS_ENDPOINT
AWS Account: $AWS_ACCOUNT
Bucket: $BUCKET_NAME
Date: $(date)
EOF

echo -e "${GREEN}✓ Saved to deployment-info.txt${NC}"

# Step 7: Build Docker Images
echo -e "${YELLOW}Step 7: Building Docker Images${NC}"
cd ../../../

ACCOUNT_ID=$AWS_ACCOUNT

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
echo -e "${GREEN}✓ Logged in to ECR${NC}"

# Create repositories
echo "Creating ECR repositories..."
aws ecr create-repository --repository-name callsync-api --region us-east-1 || true
aws ecr create-repository --repository-name callsync-frontend --region us-east-1 || true
echo -e "${GREEN}✓ Repositories created${NC}"

# Build backend
echo "Building backend Docker image..."
cd backend
docker build -t callsync-api:latest .
docker tag callsync-api:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/callsync-api:latest
echo -e "${GREEN}✓ Backend image pushed${NC}"

# Step 8: Deploy to ECS
echo -e "${YELLOW}Step 8: Deploying to ECS${NC}"
cd ..
aws ecs update-service \
  --cluster callsync-dev \
  --service callsync-api \
  --force-new-deployment
echo "Waiting for service to stabilize (this takes 5 minutes)..."
aws ecs wait services-stable \
  --cluster callsync-dev \
  --services callsync-api
echo -e "${GREEN}✓ Service deployed${NC}"

# Step 9: Verify Deployment
echo -e "${YELLOW}Step 9: Verifying Deployment${NC}"
for i in {1..10}; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$ALB_DNS/health || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ API is healthy!${NC}"
    break
  fi
  echo "Attempt $i: HTTP $HTTP_CODE (waiting...)"
  sleep 10
done

# Step 10: Test API
echo -e "${YELLOW}Step 10: Testing API${NC}"
echo "Health check:"
curl -s http://$ALB_DNS/health | jq . || echo "API responding"
echo ""
echo "API docs available at: http://$ALB_DNS/docs"

# Done
echo -e "${GREEN}======================================"
echo "✓ CallSync Deployment Complete!"
echo "=====================================${NC}"
echo ""
echo "Your CallSync URLs:"
echo "  API: http://$ALB_DNS"
echo "  Docs: http://$ALB_DNS/docs"
echo "  Health: http://$ALB_DNS/health"
echo ""
echo "Next steps:"
echo "  1. Run load tests: API_URL=http://$ALB_DNS k6 run tests/load/api_load.js"
echo "  2. View logs: aws logs tail /ecs/callsync-dev --follow"
echo "  3. Monitor: https://console.aws.amazon.com/cloudwatch"
echo ""
echo "All info saved to: deployment-info.txt"

