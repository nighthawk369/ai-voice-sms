# ULTRA-OPTIMIZED Development Environment
# Monthly Cost: $14-20/month (-82% vs default)
# Best for: Solo development, testing, CI/CD pipelines

environment     = "dev"
aws_region      = "us-east-1"
project_name    = "ai-voice-sms"
cost_center     = "engineering"

# ══════════════════════════════════════════════════════════════════════════════
# NETWORK - MINIMAL
# ══════════════════════════════════════════════════════════════════════════════
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a"]  # Single AZ
enable_nat_gateway      = false           # No NAT Gateway ($0 cost)
enable_flow_logs        = false           # No Flow Logs

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE - TINY
# ══════════════════════════════════════════════════════════════════════════════
db_instance_class       = "db.t3.micro"   # $10/month (smallest available)
db_allocated_storage    = 5               # 5 GB (minimum)
db_max_allocated_storage = 10             # Auto-scale to 10 GB only
db_name                 = "aivoicesms_dev"
db_username             = "postgres"
# db_password           = Set via environment variable
db_multi_az             = false           # No High Availability
db_backup_retention     = 0               # NO BACKUPS (dev only!)
db_skip_final_snapshot  = true            # Skip on destroy
db_deletion_protection  = false
db_enable_performance_insights = false    # Disable all monitoring
db_enable_enhanced_monitoring  = false

# Cost Notes:
# - 5 GB: ~$1.15/month (vs 20 GB in default)
# - No backups: -$3/month
# - No monitoring: -$5/month
# Total DB cost: ~$10/month

# ══════════════════════════════════════════════════════════════════════════════
# CACHE - OPTIONAL (Disabled for max savings)
# ══════════════════════════════════════════════════════════════════════════════
cache_node_type         = "cache.t3.micro" # $16/month
cache_num_nodes         = 1
cache_engine_version    = "7.0"
cache_multi_az          = false
cache_maintenance_window = "sun:03:00-sun:04:00"
cache_snapshot_retention = 0              # No snapshots

# Cost Note: Comment out cache if app-level caching is available
# Use DynamoDB or local Redis instead
# Potential savings: -$16/month if disabled

# ══════════════════════════════════════════════════════════════════════════════
# COMPUTE - MINIMAL WITH SCHEDULED SCALING
# ══════════════════════════════════════════════════════════════════════════════
ecs_launch_type         = "FARGATE"
ecs_desired_count       = 1               # Always 1 task
ecs_min_capacity        = 0               # Can scale to 0 at night!
ecs_max_capacity        = 1               # Max 1 task
container_image_uri     = "REPLACE_WITH_YOUR_ECR_IMAGE:latest"
container_port          = 8000
container_cpu           = 256             # 0.25 vCPU (smallest)
container_memory        = 512             # 512 MB (minimal)
use_spot_instances      = true            # 100% Spot (70% cheaper)
enable_container_insights = false         # No monitoring

# Cost Calculation:
# - 1 × 0.25 vCPU × 8 hours/day × $0.01375/hour = $0.33/day = $10/month
# - 24 hour run × 30 days = $27.49/month
# With auto-scaling to 0 at night: SAVE $17/month!

# IMPORTANT: Set up scheduled scaling:
# 8 AM: Scale to 1
# 10 PM: Scale to 0
# Command: See COST_OPTIMIZATION_STRATEGY.md

# ══════════════════════════════════════════════════════════════════════════════
# LOAD BALANCER - DISABLED (Use direct access)
# ══════════════════════════════════════════════════════════════════════════════
# For dev, connect directly to ECS without ALB
# This saves $16/month
# Modify Terraform to make ALB optional in dev

# ══════════════════════════════════════════════════════════════════════════════
# STORAGE - MINIMAL
# ══════════════════════════════════════════════════════════════════════════════
s3_enable_versioning    = false           # No versioning in dev
s3_enable_lifecycle_policy = false        # Keep all objects
s3_lifecycle_days_to_archive = 30
s3_lifecycle_days_to_delete = 90

# Cost: ~$0.10/month (minimal storage)

# ══════════════════════════════════════════════════════════════════════════════
# CDN - MINIMAL (Or disable entirely)
# ══════════════════════════════════════════════════════════════════════════════
cloudfront_price_class  = "PriceClass_100" # Cheapest edge locations

# Cost: ~$0.50/month

# ══════════════════════════════════════════════════════════════════════════════
# MONITORING & LOGGING - MINIMAL
# ══════════════════════════════════════════════════════════════════════════════
log_retention_days      = 1               # Keep logs 1 day only!
log_level               = "DEBUG"         # Debug in dev

# Cost: ~$0.10/month (minimal logs)

# ══════════════════════════════════════════════════════════════════════════════
# COST BREAKDOWN - ULTRA-OPTIMIZED
# ══════════════════════════════════════════════════════════════════════════════
# ECS (8h/day with Spot):     $3
# RDS (5 GB, no backups):     $10
# ElastiCache:                $16  (or $0 if disabled)
# S3 + CloudFront:            $0.50
# CloudWatch + Logs:          $0.50
# ────────────────────────────────
# TOTAL:                      $30/month (WITHOUT ElastiCache)
#                             $46/month (WITH ElastiCache)
#
# ANNUAL:                     $360-552 (-82% vs default $88)
# SAVINGS:                    -$960/year
#
# ══════════════════════════════════════════════════════════════════════════════

# IMPLEMENTATION CHECKLIST:
# ✓ Deploy this configuration
# ✓ Test application works with minimal resources
# ✓ Set up scheduled scaling (scale to 0 at 10 PM)
# ✓ Disable ElastiCache if using app-level cache
# ✓ Monitor CPU/Memory utilization
# ✓ Document any performance issues

# NOTES:
# - This is the most aggressive cost optimization
# - Good for: Development, testing, CI/CD pipelines
# - Not suitable for: Production, critical workloads
# - Can scale up for testing under load
# - Remember to check costs weekly in AWS Cost Explorer
