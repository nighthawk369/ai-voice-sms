# Global Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-voice-sms"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "engineering"
}

# VPC Variables
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (costs money, disable for dev)"
  type        = bool
  default     = false
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs (adds cost)"
  type        = bool
  default     = false
}

# RDS Database Variables
variable "db_instance_class" {
  description = "RDS instance class (cost optimization)"
  type        = string
  # dev: db.t3.micro ($31/month), staging: db.t3.small ($62/month), prod: db.t3.medium ($251/month)
  default = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "aivoicesms"
}

variable "db_username" {
  description = "Database admin username"
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "db_password" {
  description = "Database admin password"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for HA (costs 2x, disable for dev/staging)"
  type        = bool
  default     = false
}

variable "db_backup_retention" {
  description = "Backup retention period in days (0 to disable)"
  type        = number
  default     = 7
}

variable "db_skip_final_snapshot" {
  description = "Skip final snapshot on destroy (safe for dev only)"
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = false
}

variable "db_enable_performance_insights" {
  description = "Enable Performance Insights (adds cost)"
  type        = bool
  default     = false
}

variable "db_enable_enhanced_monitoring" {
  description = "Enable Enhanced Monitoring (adds cost)"
  type        = bool
  default     = false
}

# ElastiCache Variables
variable "cache_node_type" {
  description = "ElastiCache node type (cost optimization)"
  type        = string
  # dev: cache.t3.micro ($16/month), staging: cache.t3.small ($32/month), prod: cache.r6g.large ($130/month)
  default = "cache.t3.micro"
}

variable "cache_num_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "cache_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "cache_multi_az" {
  description = "Enable Multi-AZ for cache (adds cost)"
  type        = bool
  default     = false
}

variable "cache_maintenance_window" {
  description = "Maintenance window"
  type        = string
  default     = "sun:03:00-sun:04:00"
}

variable "cache_snapshot_retention" {
  description = "Snapshot retention limit (0 to disable)"
  type        = number
  default     = 0
}

# ECS Variables
variable "ecs_launch_type" {
  description = "ECS launch type (FARGATE or EC2)"
  type        = string
  default     = "FARGATE"
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks"
  type        = number
  default     = 1
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks"
  type        = number
  default     = 3
}

variable "container_image_uri" {
  description = "Docker image URI"
  type        = string
  default     = "nginx:latest"  # Replace with your image
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "container_cpu" {
  description = "Container CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Container memory in MB"
  type        = number
  default     = 512
}

variable "use_spot_instances" {
  description = "Use Fargate Spot for cost savings (70% cheaper, but can be interrupted)"
  type        = bool
  default     = false
}

variable "enable_container_insights" {
  description = "Enable ECS Container Insights (adds cost)"
  type        = bool
  default     = false
}

# ALB Variables
variable "alb_deletion_protection" {
  description = "Enable deletion protection for ALB"
  type        = bool
  default     = false
}

# S3 Variables
variable "s3_enable_versioning" {
  description = "Enable S3 versioning (adds storage cost)"
  type        = bool
  default     = false
}

variable "s3_enable_lifecycle_policy" {
  description = "Enable S3 lifecycle policy for cost optimization"
  type        = bool
  default     = true
}

variable "s3_lifecycle_days_to_archive" {
  description = "Days before archiving to Glacier"
  type        = number
  default     = 30
}

variable "s3_lifecycle_days_to_delete" {
  description = "Days before permanent deletion"
  type        = number
  default     = 90
}

# CloudFront Variables
variable "cloudfront_price_class" {
  description = "CloudFront price class (PriceClass_100=cheapest, PriceClass_All=most coverage)"
  type        = string
  default     = "PriceClass_100"
}

# Monitoring Variables
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7  # Reduce for cost savings (default AWS: 365)
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}
