terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state (S3 + DynamoDB)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "ai-voice-sms/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CostCenter  = var.cost_center
      CreatedAt   = timestamp()
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  environment   = var.environment
  project_name  = var.project_name
  vpc_cidr      = var.vpc_cidr
  azs           = var.availability_zones
  enable_nat    = var.enable_nat_gateway
  enable_flow_logs = var.enable_flow_logs
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"

  environment  = var.environment
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}

# RDS Module
module "rds" {
  source = "./modules/rds"

  environment         = var.environment
  project_name        = var.project_name
  db_instance_class   = var.db_instance_class
  allocated_storage   = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  subnet_ids          = module.vpc.private_subnet_ids
  security_group_ids  = [module.security_groups.rds_sg_id]

  multi_az            = var.db_multi_az
  backup_retention    = var.db_backup_retention
  skip_final_snapshot = var.db_skip_final_snapshot
  deletion_protection = var.db_deletion_protection

  enable_performance_insights = var.db_enable_performance_insights
  enable_enhanced_monitoring  = var.db_enable_enhanced_monitoring
}

# ElastiCache Module
module "elasticache" {
  source = "./modules/elasticache"

  environment       = var.environment
  project_name      = var.project_name
  cache_node_type   = var.cache_node_type
  num_cache_nodes   = var.cache_num_nodes
  engine_version    = var.cache_engine_version
  subnet_ids        = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.elasticache_sg_id]

  automatic_failover_enabled = var.cache_multi_az
  maintenance_window = var.cache_maintenance_window
  snapshot_retention_limit = var.cache_snapshot_retention
}

# ECS Cluster Module
module "ecs_cluster" {
  source = "./modules/ecs"

  environment   = var.environment
  project_name  = var.project_name
  cluster_name  = "${var.project_name}-${var.environment}-cluster"

  # Container Insights for monitoring (optional, adds small cost)
  enable_container_insights = var.enable_container_insights
}

# ALB Module
module "alb" {
  source = "./modules/alb"

  environment      = var.environment
  project_name     = var.project_name
  vpc_id           = module.vpc.vpc_id
  subnet_ids       = module.vpc.public_subnet_ids
  security_group_ids = [module.security_groups.alb_sg_id]

  enable_deletion_protection = var.alb_deletion_protection
  enable_http2              = true
  enable_cross_zone_load_balancing = true
}

# ECS Service Module
module "ecs_service" {
  source = "./modules/ecs_service"

  environment          = var.environment
  project_name         = var.project_name
  cluster_id           = module.ecs_cluster.cluster_id
  cluster_name         = module.ecs_cluster.cluster_name
  service_name         = "${var.project_name}-api"

  # Container Config
  image_uri            = var.container_image_uri
  container_port       = var.container_port
  container_memory     = var.container_memory
  container_cpu        = var.container_cpu

  # Networking
  subnet_ids           = module.vpc.private_subnet_ids
  security_group_ids   = [module.security_groups.ecs_sg_id]

  # Scaling
  desired_count        = var.ecs_desired_count
  min_capacity         = var.ecs_min_capacity
  max_capacity         = var.ecs_max_capacity

  # Use Fargate Spot for non-critical environments (saves 70%)
  launch_type          = var.ecs_launch_type
  capacity_provider_strategy = var.use_spot_instances ? [
    {
      capacity_provider = "FARGATE_SPOT"
      weight            = 70  # 70% spot
      base              = var.ecs_min_capacity
    },
    {
      capacity_provider = "FARGATE"
      weight            = 30  # 30% on-demand
    }
  ] : []

  # ALB Integration
  alb_target_group_arn = module.alb.target_group_arn

  # Environment Variables
  environment_variables = {
    DATABASE_URL        = "postgresql://${var.db_username}:${var.db_password}@${module.rds.endpoint}:5432/${var.db_name}"
    REDIS_URL           = "redis://${module.elasticache.endpoint}:6379"
    ENVIRONMENT         = var.environment
    LOG_LEVEL           = var.log_level
  }

  # Secrets (stored in Secrets Manager)
  secrets = {
    SECRET_KEY          = "${var.project_name}/${var.environment}/secret_key"
    TWILIO_ACCOUNT_SID  = "${var.project_name}/${var.environment}/twilio_account_sid"
    TWILIO_AUTH_TOKEN   = "${var.project_name}/${var.environment}/twilio_auth_token"
    OPENAI_API_KEY      = "${var.project_name}/${var.environment}/openai_api_key"
    STRIPE_SECRET_KEY   = "${var.project_name}/${var.environment}/stripe_secret_key"
  }

  depends_on = [module.rds, module.elasticache]
}

# S3 Module (for uploads, backups)
module "s3" {
  source = "./modules/s3"

  environment  = var.environment
  project_name = var.project_name

  enable_versioning         = var.s3_enable_versioning
  enable_lifecycle_policy   = var.s3_enable_lifecycle_policy
  lifecycle_days_to_archive = var.s3_lifecycle_days_to_archive
  lifecycle_days_to_delete  = var.s3_lifecycle_days_to_delete
  enable_encryption         = true
}

# CloudFront CDN Module
module "cloudfront" {
  source = "./modules/cloudfront"

  environment  = var.environment
  project_name = var.project_name

  s3_bucket_domain_name = module.s3.bucket_regional_domain_name
  alb_domain_name       = module.alb.dns_name

  # Cost optimization: Use fewer edge locations for dev/staging
  price_class = var.cloudfront_price_class

  enable_compression = true
  enable_cache_policy = true
}

# CloudWatch Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  environment      = var.environment
  project_name     = var.project_name

  # Alarms
  create_cost_anomaly_detector = var.environment == "production"

  # Log Groups
  ecs_log_group_name = "/aws/ecs/${var.project_name}-${var.environment}"
  log_retention_days = var.log_retention_days
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.dns_name
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "elasticache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.endpoint
  sensitive   = true
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.cloudfront.domain_name
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = module.ecs_cluster.cluster_name
}

output "ecs_service_name" {
  description = "ECS Service name"
  value       = module.ecs_service.service_name
}
