#!/bin/bash
# CallSync - Start AWS Infrastructure
# Deploys all AWS resources (VPC, RDS, ECS, ALB, etc.)
# Takes ~20 minutes

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  CallSync - Start AWS Infrastructure${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
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

# Change to Terraform directory
cd infrastructure/terraform/aws

# Check if state file exists
STATE_EXISTS=0
if aws s3 ls "s3://callsync-terraform-state-$AWS_ACCOUNT/callsync/dev/terraform.tfstate" 2>/dev/null; then
  STATE_EXISTS=1
  echo -e "${GREEN}✓ Terraform state found${NC}"
else
  echo -e "${YELLOW}⚠ Terraform state not found - first time deployment${NC}"
fi
echo ""

# Terraform plan
echo -e "${YELLOW}Planning infrastructure...${NC}"
terraform plan -var-file="environments/dev-ultra-optimized.tfvars" -out=tfplan
echo ""

# Confirm before deploying
echo -e "${YELLOW}Review the plan above. Deploy infrastructure?${NC}"
read -p "Type 'yes' to continue: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo -e "${RED}Deployment cancelled${NC}"
  exit 1
fi
echo ""

# Deploy
echo -e "${YELLOW}Deploying infrastructure (15-20 minutes)...${NC}"
terraform apply tfplan
echo ""

# Get outputs
echo -e "${YELLOW}Retrieving deployment information...${NC}"
ALB_DNS=$(terraform output -raw alb_dns_name)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

# Save info
cat > infrastructure-running.txt << INFEOF
CallSync Infrastructure Started
==============================
Started: $(date)
AWS Account: $AWS_ACCOUNT

API Endpoints:
  ALB DNS: $ALB_DNS
  API URL: http://$ALB_DNS
  API Docs: http://$ALB_DNS/docs
  Health: http://$ALB_DNS/health

Database:
  RDS Endpoint: $RDS_ENDPOINT

Cache:
  Redis Endpoint: $REDIS_ENDPOINT

Cost: ~$32/month while running

To stop infrastructure:
  ./STOP_INFRASTRUCTURE.sh

To check status:
  ./INFRASTRUCTURE_STATUS.sh
INFEOF

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Infrastructure Started!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Your CallSync API:${NC}"
echo -e "  ${BLUE}http://$ALB_DNS${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Deploy application: ./DEPLOY_AUTOMATED.sh"
echo "  2. Monitor logs: aws logs tail /ecs/callsync-dev --follow"
echo "  3. Stop when done: ./STOP_INFRASTRUCTURE.sh"
echo ""
echo "Info saved to: infrastructure-running.txt"
