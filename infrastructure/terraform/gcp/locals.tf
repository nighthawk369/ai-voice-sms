# Common locals used throughout the configuration

locals {
  # Service naming convention
  service_name = "${var.app_name}-${var.environment}"

  # Common labels applied to all resources
  common_labels = merge(
    var.labels,
    {
      environment = var.environment
      application = var.app_name
      managed_by  = "terraform"
      created_at  = timestamp()
    }
  )

  # Database configuration
  database_config = {
    version           = var.database_version
    instance_type     = var.database_instance_type
    database_name     = "ai_platform"
    app_user          = "app_user"
    is_production     = var.environment == "production"
    enable_backups    = var.environment != "dev"
    backup_retention  = var.environment == "production" ? 30 : 7
    enable_ha         = var.environment == "production"
  }

  # Redis configuration
  redis_config = {
    memory_size_gb = var.redis_memory_size
    tier           = var.redis_tier
    version        = "7.0"
    is_production  = var.environment == "production"
  }

  # Cloud Run API configuration
  api_config = {
    name          = "${local.service_name}-api"
    image_path    = "${var.region}-docker.pkg.dev/${var.project_id}/$${docker_repo}/api:latest"
    memory        = "${var.api_memory}Mi"
    cpu           = var.api_cpu
    max_instances = var.api_max_instances
    timeout       = 300
  }

  # Cloud Run Web configuration
  web_config = {
    name          = "${local.service_name}-web"
    image_path    = "${var.region}-docker.pkg.dev/${var.project_id}/$${docker_repo}/web:latest"
    memory        = "${var.web_memory}Mi"
    cpu           = var.web_cpu
    max_instances = var.web_max_instances
    timeout       = 300
  }

  # Storage configuration
  storage_config = {
    documents_retention_days  = 90
    recordings_retention_days = 30
    exports_retention_days    = 7
    enable_versioning         = var.environment == "production"
    force_destroy             = var.environment != "production"
  }

  # Security configuration
  security_config = {
    require_ssl       = var.environment == "production"
    enable_iam_auth   = var.environment == "production"
    rate_limit        = 100  # requests per minute per IP
    rate_limit_window = 60   # seconds
  }

  # Backup and recovery configuration
  backup_config = {
    enabled           = local.database_config.enable_backups
    daily_backup_time = "03:00"  # UTC
    retention_days    = local.database_config.backup_retention
  }

  # Resource naming
  resource_names = {
    vpc_network          = "${local.service_name}-network"
    vpc_subnet           = "${local.service_name}-subnet"
    cloud_sql_instance   = "${local.service_name}-db"
    redis_instance       = "${local.service_name}-redis"
    artifacts_repo       = "${local.service_name}-docker"
    cloud_armor_policy   = "${local.service_name}-cloud-armor"
    scheduler_backup_job = "${local.service_name}-backup-scheduler"
    secret_db_password   = "${local.service_name}-db-password"
    secret_jwt           = "${local.service_name}-jwt-secret"
  }

  # Feature flags
  features = {
    enable_cloud_armor     = true
    enable_monitoring      = true
    enable_cloud_scheduler = var.environment != "dev"
    enable_cdn             = var.environment == "production"
  }

  # Environment-specific settings
  env_settings = {
    dev = {
      instance_tier         = "db-f1-micro"
      redis_memory_gb       = 1
      api_memory_mi         = 512
      api_cpu               = "1"
      api_max_instances     = 5
      web_memory_mi         = 256
      web_cpu               = "1"
      web_max_instances     = 3
      enable_backups        = false
      require_ssl           = false
    }
    staging = {
      instance_tier         = "db-n1-standard-1"
      redis_memory_gb       = 2
      api_memory_mi         = 1024
      api_cpu               = "2"
      api_max_instances     = 10
      web_memory_mi         = 512
      web_cpu               = "2"
      web_max_instances     = 8
      enable_backups        = true
      require_ssl           = true
    }
    production = {
      instance_tier         = "db-n1-standard-2"
      redis_memory_gb       = 4
      api_memory_mi         = 2048
      api_cpu               = "4"
      api_max_instances     = 50
      web_memory_mi         = 1024
      web_cpu               = "2"
      web_max_instances     = 30
      enable_backups        = true
      require_ssl           = true
    }
  }
}
