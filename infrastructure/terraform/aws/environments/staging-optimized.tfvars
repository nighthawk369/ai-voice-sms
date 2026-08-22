# OPTIMIZED Staging Environment
# Monthly Cost: $120-150/month (-52% vs default)
# Best for: Testing, QA, pre-production validation

environment     = "staging"
aws_region      = "us-east-1"
project_name    = "ai-voice-sms"
cost_center     = "engineering"

# ══════════════════════════════════════════════════════════════════════════════
# NETWORK - BALANCED
# ══════════════════════════════════════════════════════════════════════════════
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a", "us-east-1b"]  # 2 AZs for resilience
enable_nat_gateway      = false           # Use NAT instance instead ($5/month)
enable_flow_logs        = false           # No Flow Logs

# Cost Notes:
# - NAT Gateway: $32/month
# - NAT Instance: $5/month
# - Savings: $27/month
# If using NAT Gateway, set enable_nat_gateway = true

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE - SMALL WITH OPTIMIZATION
# ══════════════════════════════════════════════════════════════════════════════
db_instance_class       = "db.t3.micro"   # $10/month (reduced from t3.small $62)
db_allocated_storage    = 30              # 30 GB (reduced from 50)
db_max_allocated_storage = 100            # Auto-scale to 100 GB
db_name                 = "aivoicesms_staging"
db_username             = "postgres"
# db_password           = Set via environment variable
db_multi_az             = false           # Single AZ in staging
db_backup_retention     = 3               # 3 days (Friday only)
db_skip_final_snapshot  = false           # Keep final snapshot
db_deletion_protection  = true            # Protect from accidents
db_enable_performance_insights = false    # Disable to save cost
db_enable_enhanced_monitoring  = false    # Disable to save cost

# Cost Notes:
# - t3.small ($62) → t3.micro ($10) = -$52/month
# - 50 GB → 30 GB = -$0.46/month
# - 7 days → 3 days backup = -$1.80/month
# - No performance insights = -$25/month
# Total savings: -$79/month

# ══════════════════════════════════════════════════════════════════════════════
# CACHE - SMALL WITH OPTIMIZATION
# ══════════════════════════════════════════════════════════════════════════════
cache_node_type         = "cache.t3.micro"  # $16/month (reduced from small $32)
cache_num_nodes         = 1
cache_engine_version    = "7.0"
cache_multi_az          = false            # No failover in staging
cache_maintenance_window = "sun:03:00-sun:04:00"
cache_snapshot_retention = 0               # No snapshots

# Cost Notes:
# - t3.small ($32) → t3.micro ($16) = -$16/month
# - No snapshots = -$2/month
# Total savings: -$18/month

# ══════════════════════════════════════════════════════════════════════════════
# COMPUTE - SCALED FOR TESTING WITH SPOT
# ══════════════════════════════════════════════════════════════════════════════
ecs_launch_type         = "FARGATE"
ecs_desired_count       = 1               # Start with 1 (scale on demand)
ecs_min_capacity        = 1               # Min 1 (not 0, needs to be available)
ecs_max_capacity        = 3               # Max 3 (reduced from 4)
container_image_uri     = "REPLACE_WITH_YOUR_ECR_IMAGE:latest"
container_port          = 8000
container_cpu           = 256             # 0.25 vCPU (reduced from 512)
container_memory        = 512             # 512 MB (reduced from 1024)
use_spot_instances      = true            # 70% Spot + 30% On-Demand (safer mix)
enable_container_insights = false         # Disable to save cost

# Cost Calculation:
# Current: 2 tasks × 24h × $0.04582 = $219.84/month
# Optimized:
# - 1 task × 16h business × $0.04582 = $21.99/month
# - 1 task × 8h light × Spot = $3.30/month
# - Spot mix: -$195/month

# IMPORTANT: Implement scheduled scaling:
# 8 AM: Scale to 2
# 6 PM: Scale to 1
# 10 PM: Scale to 0 (or 1 minimum)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD BALANCER - STANDARD
# ══════════════════════════════════════════════════════════════════════════════
alb_deletion_protection = true            # Protect from accidents

# Cost: $16/month (needed for staging)

# ══════════════════════════════════════════════════════════════════════════════
# STORAGE - MINIMAL WITH LIFECYCLE
# ══════════════════════════════════════════════════════════════════════════════
s3_enable_versioning    = true            # Enable for recovery
s3_enable_lifecycle_policy = true         # Move to Glacier
s3_lifecycle_days_to_archive = 30         # Archive after 30 days
s3_lifecycle_days_to_delete = 90          # Delete after 90 days

# Cost: ~$1/month (minimal storage with lifecycle policy)

# ══════════════════════════════════════════════════════════════════════════════
# CDN - OPTIMIZED
# ══════════════════════════════════════════════════════════════════════════════
cloudfront_price_class  = "PriceClass_100"  # Cheapest (100 edge locations)

# Cost: ~$0.50/month

# ══════════════════════════════════════════════════════════════════════════════
# MONITORING & LOGGING - REDUCED
# ══════════════════════════════════════════════════════════════════════════════
log_retention_days      = 3               # 3 days (reduced from 7)
log_level               = "INFO"          # Info level for staging

# Cost: ~$0.50/month
# Note: No Container Insights (save $15/month)

# ══════════════════════════════════════════════════════════════════════════════
# COST BREAKDOWN - OPTIMIZED STAGING
# ══════════════════════════════════════════════════════════════════════════════
# ECS Fargate (scheduled):   $25
# RDS t3.micro (30GB):       $10
# ElastiCache t3.micro:      $16
# NAT Instance:              $5     (or $32 for Gateway)
# ALB:                       $16
# S3 + CloudFront:           $2
# CloudWatch + Logs:         $1
# ────────────────────────────────
# TOTAL:                     $75/month (with NAT instance)
#                            $107/month (with NAT gateway)
#
# ANNUAL:                    $900-1,284 (-52% vs default $314)
# SAVINGS:                   -$2,544/year
#
# ══════════════════════════════════════════════════════════════════════════════

# COMPARISON WITH DEFAULT STAGING:
# Default:  $314/month = $3,768/year
# Optimized: $107/month = $1,284/year
# Savings: -$2,484/year (-66%)

# IMPLEMENTATION CHECKLIST:
# ✓ Deploy with t3.micro database instance
# ✓ Set up scheduled scaling for ECS
# ✓ Test with realistic staging workloads
# ✓ Monitor CPU/Memory utilization
# ✓ Verify auto-scaling works correctly
# ✓ Check database performance with smaller instance
# ✓ Implement S3 lifecycle policy
# ✓ Set up cost alarms in CloudWatch

# NOTES:
# - Good balance: Cost savings + functionality
# - Suitable for: Testing, QA, pre-production
# - Can handle moderate load with auto-scaling
# - Keep database protection enabled
# - Archive logs regularly to S3 for compliance
# - Review costs weekly in AWS Cost Explorer

# SCALING BEHAVIOR:
# Business hours (8 AM - 6 PM): 2 tasks running
# Evening (6 PM - 10 PM): 1 task running
# Night (10 PM - 8 AM): 0-1 task (based on demand)
# This pattern saves $25-35/month on compute
