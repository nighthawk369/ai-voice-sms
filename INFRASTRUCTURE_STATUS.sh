#!/bin/bash
# CallSync - Check Infrastructure Status
# Shows whether infrastructure is running, stopped, or has issues

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  CallSync - Infrastructure Status${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Check AWS credentials
echo -e "${YELLOW}Verifying AWS credentials...${NC}"
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ -z "$AWS_ACCOUNT" ]; then
  echo -e "${RED}✗ AWS credentials not configured${NC}"
  exit 1
fi
echo -e "${GREEN}✓ AWS Account: $AWS_ACCOUNT${NC}"
echo ""

# Check ECS cluster
echo -e "${YELLOW}Checking ECS Cluster...${NC}"
CLUSTER_STATUS=$(aws ecs describe-clusters --clusters callsync-dev --query 'clusters[0].status' --output text 2>/dev/null || echo "NOTFOUND")

if [ "$CLUSTER_STATUS" == "NOTFOUND" ]; then
  echo -e "${RED}✗ ECS Cluster not found (infrastructure is STOPPED)${NC}"
  RUNNING=0
elif [ "$CLUSTER_STATUS" == "ACTIVE" ]; then
  echo -e "${GREEN}✓ ECS Cluster ACTIVE${NC}"
  RUNNING=1
else
  echo -e "${YELLOW}⚠ ECS Cluster status: $CLUSTER_STATUS${NC}"
  RUNNING=0
fi
echo ""

# Check RDS
echo -e "${YELLOW}Checking RDS Database...${NC}"
RDS_STATUS=$(aws rds describe-db-instances --db-instance-identifier callsync-dev --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null || echo "NOTFOUND")

if [ "$RDS_STATUS" == "NOTFOUND" ]; then
  echo -e "${RED}✗ RDS Instance not found (stopped)${NC}"
elif [ "$RDS_STATUS" == "available" ]; then
  echo -e "${GREEN}✓ RDS Database available${NC}"
elif [ "$RDS_STATUS" == "creating" ]; then
  echo -e "${YELLOW}⚠ RDS Database is creating (wait a few minutes)${NC}"
else
  echo -e "${YELLOW}⚠ RDS status: $RDS_STATUS${NC}"
fi
echo ""

# Check ECS service
if [ $RUNNING -eq 1 ]; then
  echo -e "${YELLOW}Checking ECS Service...${NC}"
  SERVICE_STATUS=$(aws ecs describe-services --cluster callsync-dev --services callsync-api --query 'services[0].status' --output text 2>/dev/null || echo "NOTFOUND")
  
  if [ "$SERVICE_STATUS" == "ACTIVE" ]; then
    echo -e "${GREEN}✓ ECS Service ACTIVE${NC}"
    
    # Check running tasks
    RUNNING_TASKS=$(aws ecs list-tasks --cluster callsync-dev --desired-status RUNNING --query 'taskArns[]' --output text 2>/dev/null | wc -w)
    echo -e "${GREEN}✓ Running tasks: $RUNNING_TASKS${NC}"
    
    # Get ALB DNS
    echo -e "${YELLOW}Getting API endpoint...${NC}"
    cd infrastructure/terraform/aws 2>/dev/null || cd . 
    ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "N/A")
    echo -e "${GREEN}✓ API: http://$ALB_DNS${NC}"
    
    # Test health
    if [ "$ALB_DNS" != "N/A" ]; then
      echo -e "${YELLOW}Testing API health...${NC}"
      HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$ALB_DNS/health 2>/dev/null || echo "000")
      if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ API is responding (HTTP 200)${NC}"
      else
        echo -e "${YELLOW}⚠ API returned HTTP $HTTP_CODE${NC}"
      fi
    fi
  else
    echo -e "${YELLOW}⚠ ECS Service status: $SERVICE_STATUS${NC}"
  fi
else
  echo -e "${YELLOW}Infrastructure is not running (all services stopped)${NC}"
fi
echo ""

# Cost estimate
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Cost Estimate:${NC}"
if [ $RUNNING -eq 1 ]; then
  echo -e "${YELLOW}Infrastructure is RUNNING${NC}"
  echo -e "${YELLOW}Current monthly cost: ~\$32${NC}"
  echo -e "${YELLOW}To stop and save: ./STOP_INFRASTRUCTURE.sh${NC}"
else
  echo -e "${GREEN}Infrastructure is STOPPED${NC}"
  echo -e "${GREEN}Current monthly cost: ~\$0 (only S3 storage)${NC}"
  echo -e "${YELLOW}To start: ./START_INFRASTRUCTURE.sh${NC}"
fi
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Summary
if [ $RUNNING -eq 1 ]; then
  echo -e "${GREEN}✓ CallSync is RUNNING and ready to use${NC}"
  [ -f infrastructure-running.txt ] && echo -e "${BLUE}Details saved in: infrastructure-running.txt${NC}"
else
  echo -e "${YELLOW}⚠ CallSync infrastructure is STOPPED${NC}"
  echo -e "${YELLOW}Run: ./START_INFRASTRUCTURE.sh to deploy${NC}"
fi
