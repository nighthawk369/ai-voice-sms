# Production Environment Configuration - HIGH AVAILABILITY + COST OPTIMIZATION
# Monthly Cost: ~$2,400-2,800 (optimized with Reserved Instances)

environment     = "production"
aws_region      = "us-east-1"
project_name    = "ai-voice-sms"
cost_center     = "engineering"

# VPC - Full setup with redundancy
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a", "us-east-1b", "us-east-1c"]  # 3 AZs for HA
enable_nat_gateway      = true            # Required for outbound traffic
enable_flow_logs        = true            # Enable for audit/compliance (optional: ~$5-10/month)

# RDS - Production-grade instance with HA
db_instance_class       = "db.t3.medium"  # $251/month (or use reserved instance for -30%)
db_allocated_storage    = 100             # 100 GB
db_max_allocated_storage = 500            # Auto-scale to 500 GB
db_name                 = "aivoicesms_prod"
db_username             = "postgres"
# db_password           = Set via environment variable or AWS Secrets Manager
db_multi_az             = true            # Multi-AZ for HA (doubles cost to ~$500/month, but worth it)
db_backup_retention     = 30              # 30-day backups
db_skip_final_snapshot  = false           # Always keep final snapshot
db_deletion_protection  = true            # Prevent accidental deletion
db_enable_performance_insights = true     # Enable for monitoring (~$25/month)
db_enable_enhanced_monitoring  = true     # Enable detailed metrics

# ElastiCache - Production-grade with HA
cache_node_type         = "cache.r6g.large" # $130/month (or use reserved for -30%)
cache_num_nodes         = 2               # At least 2 for failover
cache_engine_version    = "7.0"
cache_multi_az          = true            # Multi-AZ for HA
cache_maintenance_window = "sun:03:00-sun:04:00"
cache_snapshot_retention = 7              # Weekly snapshots

# ECS - Production setup with auto-scaling
ecs_launch_type         = "FARGATE"
ecs_desired_count       = 3               # 3 tasks minimum
ecs_min_capacity        = 3               # Always run 3 instances
ecs_max_capacity        = 10              # Scale to 10 under heavy load
container_image_uri     = "REPLACE_WITH_YOUR_ECR_IMAGE:latest"
container_port          = 8000
container_cpu           = 1024            # 1 vCPU per task
container_memory        = 2048            # 2 GB per task
use_spot_instances      = false           # Only use On-Demand (reliability > cost savings)
enable_container_insights = true          # Enable for monitoring

# ALB - Production setup
alb_deletion_protection = true            # Prevent accidental deletion

# S3 - Full production setup
s3_enable_versioning    = true            # Enable versioning for data protection
s3_enable_lifecycle_policy = true         # Cost optimization with lifecycle
s3_lifecycle_days_to_archive = 30         # Move to Glacier after 30 days
s3_lifecycle_days_to_delete = 180         # Delete after 180 days

# CloudFront - Global distribution
cloudfront_price_class  = "PriceClass_All" # All edge locations (best performance)

# Monitoring - Comprehensive
log_retention_days      = 30              # Keep logs for 30 days
log_level               = "WARNING"       # Warning level in production

# Cost Optimization Summary (WITH RESERVED INSTANCES):
# ✓ RDS: db.t3.medium with 1-year reserved instance (-30%) = $176/month
# ✓ ElastiCache: Multi-AZ (-30% with reserved) = $91/month
# ✓ ECS: On-Demand for reliability, no Spot (safer)
# ✓ Auto-scaling: Scale down at night (save ~20%)
# ✓ S3: Lifecycle policy to Glacier (save ~80% on old objects)
#
# Base Cost: $3,463/month
# With Reserved Instances (-30%): ~$2,424/month
# With Spot on non-critical (-20%): ~$2,080/month
#
# RECOMMENDATION: Buy Reserved Instances for RDS + ElastiCache (1-3 year term)
# This saves ~$10,000-15,000 per year vs on-demand pricing

# AWS Pricing Tips for Production:
# 1. RDS Reserved Instances: Save 30-40% by committing to 1-3 year terms
# 2. ElastiCache Reserved Instances: Save 30-40%
# 3. ECS Capacity Reservations: Guarantee capacity at lower rates
# 4. CloudFront: Use cheaper price class for non-critical regions
# 5. S3: Lifecycle policies + Intelligent-Tiering save 60-80%
# 6. NAT Gateway: Consider NAT instance instead (~$5/month vs $32/month)
# 7. CloudWatch: Set up alarms to auto-scale down at night

# Next Step: Create AWS Cost Explorer dashboard to monitor actual spending
