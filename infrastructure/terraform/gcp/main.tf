# Locals for common naming
locals {
  service_name = "${var.app_name}-${var.environment}"
  labels = merge(
    var.labels,
    {
      environment = var.environment
      application = var.app_name
    }
  )
}

# Random suffix for global unique names
resource "random_id" "suffix" {
  byte_length = 4
}

# ============================================================
# VPC & Networking
# ============================================================

resource "google_compute_network" "main" {
  name                    = "${local.service_name}-network"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "main" {
  name          = "${local.service_name}-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_logs_enabled    = true
  }
}

# ============================================================
# Cloud SQL - PostgreSQL Database
# ============================================================

resource "google_sql_database_instance" "main" {
  name               = "${local.service_name}-db-${random_id.suffix.hex}"
  database_version   = "POSTGRES_${var.database_version}"
  region             = var.region
  deletion_protection = var.environment == "production"

  settings {
    tier              = var.database_instance_type
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "production"
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.main.id
      require_ssl     = var.environment == "production"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "main" {
  name     = "ai_platform"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "app" {
  name     = "app_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
  type     = "BUILT_IN"
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Private VPC connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${local.service_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# ============================================================
# Cloud Memorystore - Redis Cache
# ============================================================

resource "google_redis_instance" "cache" {
  name           = "${local.service_name}-redis"
  memory_size_gb = var.redis_memory_size
  tier           = var.redis_tier
  region         = var.region

  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  redis_version      = "7.0"
  display_name       = "${local.service_name} Redis Cache"

  labels = local.labels
}

# ============================================================
# Cloud Storage Buckets
# ============================================================

resource "google_storage_bucket" "documents" {
  name          = "${local.service_name}-documents-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  versioning {
    enabled = var.environment == "production"
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

resource "google_storage_bucket" "recordings" {
  name          = "${local.service_name}-recordings-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  versioning {
    enabled = var.environment == "production"
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

resource "google_storage_bucket" "exports" {
  name          = "${local.service_name}-exports-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

# ============================================================
# Secret Manager
# ============================================================

resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.service_name}-db-password"
  labels    = local.labels

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${local.service_name}-jwt-secret"
  labels    = local.labels

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}

# ============================================================
# Service Accounts
# ============================================================

resource "google_service_account" "api" {
  account_id   = "${local.service_name}-api"
  display_name = "${local.service_name} API Service Account"
}

resource "google_service_account" "web" {
  account_id   = "${local.service_name}-web"
  display_name = "${local.service_name} Web Service Account"
}

# Grant Cloud SQL Client role
resource "google_project_iam_member" "api_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api.email}"
}

# Grant Secret Accessor role
resource "google_secret_manager_secret_iam_member" "api_db_password" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

resource "google_secret_manager_secret_iam_member" "api_jwt_secret" {
  secret_id = google_secret_manager_secret.jwt_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}

# Grant Storage Object Admin role
resource "google_storage_bucket_iam_member" "api_documents" {
  bucket = google_storage_bucket.documents.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.api.email}"
}

resource "google_storage_bucket_iam_member" "api_recordings" {
  bucket = google_storage_bucket.recordings.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.api.email}"
}

resource "google_storage_bucket_iam_member" "api_exports" {
  bucket = google_storage_bucket.exports.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.api.email}"
}

# ============================================================
# Artifacts Registry for Docker Images
# ============================================================

resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = "${local.service_name}-docker"
  description   = "Docker repository for ${local.service_name}"
  format        = "DOCKER"

  labels = local.labels
}

# ============================================================
# Outputs
# ============================================================

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "database_host" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.main.private_ip_address
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.main.name
}

output "database_user" {
  description = "Database user"
  value       = google_sql_user.app.name
}

output "redis_host" {
  description = "Redis host IP"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.cache.port
}

output "storage_documents_bucket" {
  description = "Documents storage bucket"
  value       = google_storage_bucket.documents.name
}

output "storage_recordings_bucket" {
  description = "Recordings storage bucket"
  value       = google_storage_bucket.recordings.name
}

output "storage_exports_bucket" {
  description = "Exports storage bucket"
  value       = google_storage_bucket.exports.name
}

output "artifact_registry_repository" {
  description = "Artifact Registry Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}

output "api_service_account_email" {
  description = "API service account email"
  value       = google_service_account.api.email
}

output "web_service_account_email" {
  description = "Web service account email"
  value       = google_service_account.web.email
}
