# Development Environment Configuration - COST OPTIMIZED
# Monthly Cost: ~$88-100

environment     = "dev"
aws_region      = "us-east-1"
project_name    = "ai-voice-sms"
cost_center     = "engineering"

# VPC - Minimal setup for dev
vpc_cidr                = "10.0.0.0/16"
availability_zones      = ["us-east-1a"]  # Single AZ to save costs
enable_nat_gateway      = false           # NAT Gateway costs money (~$32/month)
enable_flow_logs        = false           # Flow Logs cost money

# RDS - Minimal instance
db_instance_class       = "db.t3.micro"   # $31/month
db_allocated_storage    = 20              # 20 GB
db_max_allocated_storage = 50             # Auto-scale up to 50 GB
db_name                 = "aivoicesms_dev"
db_username             = "postgres"
# db_password           = Set via environment variable or AWS Secrets Manager
db_multi_az             = false           # Single AZ (no HA needed in dev)
db_backup_retention     = 1               # Minimal backups
db_skip_final_snapshot  = true            # Safe for dev
db_deletion_protection  = false
db_enable_performance_insights = false    # Disable to save cost
db_enable_enhanced_monitoring  = false    # Disable to save cost

# ElastiCache - Minimal instance
cache_node_type         = "cache.t3.micro" # $16/month
cache_num_nodes         = 1               # Single node
cache_engine_version    = "7.0"
cache_multi_az          = false           # No HA needed
cache_maintenance_window = "sun:03:00-sun:04:00"
cache_snapshot_retention = 0              # No snapshots in dev

# ECS - Minimal setup
ecs_launch_type         = "FARGATE"
ecs_desired_count       = 1               # 1 task
ecs_min_capacity        = 1
ecs_max_capacity        = 2               # Max 2 for testing
container_image_uri     = "REPLACE_WITH_YOUR_ECR_IMAGE:latest"
container_port          = 8000
container_cpu           = 256             # 0.25 vCPU
container_memory        = 512             # 512 MB
use_spot_instances      = true            # Use 100% Spot (70% cheaper, OK for dev)
enable_container_insights = false         # Disable to save cost

# ALB
alb_deletion_protection = false

# S3
s3_enable_versioning    = false           # No versioning in dev
s3_enable_lifecycle_policy = false        # Keep all objects in dev
s3_lifecycle_days_to_archive = 30
s3_lifecycle_days_to_delete = 90

# CloudFront
cloudfront_price_class  = "PriceClass_100" # Cheapest (limited edge locations)

# Monitoring
log_retention_days      = 1               # Only keep logs for 1 day in dev
log_level               = "DEBUG"         # Debug level for development

# Cost Optimization Summary:
# ✓ Single AZ (saves ~50% on multi-region)
# ✓ Minimal instance sizes (micro)
# ✓ 100% Spot instances (saves 70%)
# ✓ No backups/snapshots
# ✓ No monitoring/Performance Insights
# ✓ Minimal log retention
# ✓ No versioning on S3
# Total: ~$88/month (vs $500+ without optimization)
