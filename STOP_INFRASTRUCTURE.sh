#!/bin/bash
# CallSync - Stop AWS Infrastructure
# Destroys all AWS resources (saves costs)
# Takes ~10 minutes
# WARNING: This deletes everything (RDS, Redis, ECS, etc.)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  CallSync - Stop AWS Infrastructure${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# WARNING
echo -e "${RED}⚠️  WARNING ⚠️${NC}"
echo -e "${RED}This will DELETE all AWS resources:${NC}"
echo -e "${RED}  - RDS Database (all data will be LOST)${NC}"
echo -e "${RED}  - Redis Cache${NC}"
echo -e "${RED}  - ECS Service${NC}"
echo -e "${RED}  - Load Balancer${NC}"
echo -e "${RED}  - VPC and Security Groups${NC}"
echo ""
echo -e "${YELLOW}But Terraform state will be preserved (stored in S3)${NC}"
echo -e "${YELLOW}You can re-deploy later with START_INFRASTRUCTURE.sh${NC}"
echo ""

# Double confirmation
read -p "Are you SURE? Type 'destroy everything' to continue: " CONFIRM
if [ "$CONFIRM" != "destroy everything" ]; then
  echo -e "${GREEN}Destruction cancelled - infrastructure remains running${NC}"
  exit 0
fi
echo ""

# Verify AWS credentials
echo -e "${YELLOW}Verifying AWS credentials...${NC}"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ -z "$AWS_ACCOUNT" ]; then
  echo -e "${RED}✗ AWS credentials not configured${NC}"
  exit 1
fi
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT${NC}"
echo ""

# Change to Terraform directory
cd infrastructure/terraform/aws

# Destroy
echo -e "${YELLOW}Destroying infrastructure (10 minutes)...${NC}"
terraform destroy -var-file="environments/dev-ultra-optimized.tfvars" -auto-approve

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Infrastructure Stopped!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Your AWS resources are now DELETED${NC}"
echo -e "${GREEN}You are no longer paying for compute (except S3 storage)${NC}"
echo ""
echo -e "${YELLOW}To restart:${NC}"
echo "  ./START_INFRASTRUCTURE.sh"
echo ""

# Cleanup local files
rm -f infrastructure-running.txt
echo "Cleaned up infrastructure-running.txt"
