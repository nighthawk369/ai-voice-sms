# Staging Environment Configuration - BALANCED APPROACH
# Monthly Cost: ~$314-350

environment     = "staging"
aws_region      = "us-east-1"
project_name    = "ai-voice-sms"
cost_center     = "engineering"

# VPC - Balanced setup
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a", "us-east-1b"]  # 2 AZs for some resilience
enable_nat_gateway      = true            # NAT Gateway for outbound traffic (~$32/month)
enable_flow_logs        = false           # Flow Logs cost money (~$5-10/month)

# RDS - Small instance with some redundancy
db_instance_class       = "db.t3.small"   # $62/month
db_allocated_storage    = 50              # 50 GB (vs 20 in dev)
db_max_allocated_storage = 200            # Auto-scale to 200 GB
db_name                 = "aivoicesms_staging"
db_username             = "postgres"
# db_password           = Set via environment variable or AWS Secrets Manager
db_multi_az             = false           # Single AZ in staging (HA not critical)
db_backup_retention     = 7               # Weekly backups
db_skip_final_snapshot  = false           # Keep final snapshot for recovery
db_deletion_protection  = true            # Protect against accidental deletion
db_enable_performance_insights = false    # Disable to save cost (~$25/month)
db_enable_enhanced_monitoring  = true     # Enable for testing (detailed metrics)

# ElastiCache - Small instance
cache_node_type         = "cache.t3.small" # $32/month
cache_num_nodes         = 1               # Single node
cache_engine_version    = "7.0"
cache_multi_az          = false           # No HA needed in staging
cache_maintenance_window = "sun:03:00-sun:04:00"
cache_snapshot_retention = 0              # No snapshots to save cost

# ECS - Moderate setup
ecs_launch_type         = "FARGATE"
ecs_desired_count       = 2               # 2 tasks
ecs_min_capacity        = 1               # Minimum 1
ecs_max_capacity        = 4               # Scale to 4 under load
container_image_uri     = "REPLACE_WITH_YOUR_ECR_IMAGE:latest"
container_port          = 8000
container_cpu           = 512             # 0.5 vCPU
container_memory        = 1024            # 1 GB
use_spot_instances      = true            # Use 70% Spot, 30% On-Demand (safer than 100% Spot)
enable_container_insights = true          # Enable for testing (~$0.50/day)

# ALB
alb_deletion_protection = true            # Protect load balancer

# S3
s3_enable_versioning    = true            # Enable versioning in staging
s3_enable_lifecycle_policy = true         # Archive old versions
s3_lifecycle_days_to_archive = 30         # Archive after 30 days
s3_lifecycle_days_to_delete = 90          # Delete after 90 days

# CloudFront
cloudfront_price_class  = "PriceClass_100" # Cheapest (OK for staging)

# Monitoring
log_retention_days      = 7               # Keep logs for a week
log_level               = "INFO"          # Info level for staging

# Cost Optimization Summary:
# ✓ 70% Spot + 30% On-Demand (safer mix)
# ✓ Small instance sizes
# ✓ 2 AZ for some resilience (not full HA)
# ✓ Minimal backups/snapshots
# ✓ Weekly log retention
# ✓ S3 versioning + lifecycle policy
# Total: ~$314/month
