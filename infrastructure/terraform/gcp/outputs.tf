# ============================================================
# Consolidated Outputs
# ============================================================

# Deployment Information
output "deployment_environment" {
  description = "Deployment environment"
  value       = var.environment
}

output "deployment_region" {
  description = "GCP region"
  value       = var.region
}

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

# Database Outputs
output "database_connection_name" {
  description = "Cloud SQL connection name for Cloud Run"
  value       = google_sql_database_instance.main.connection_name
}

output "database_host" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.main.name
}

output "database_user" {
  description = "Database user"
  value       = google_sql_user.app.name
}

output "database_password_secret" {
  description = "Secret Manager secret name for database password"
  value       = google_secret_manager_secret.db_password.id
}

# Redis Outputs
output "redis_host" {
  description = "Redis instance host IP"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.cache.port
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
  sensitive   = true
}

# Cloud Storage Outputs
output "storage_documents_bucket" {
  description = "Documents storage bucket name"
  value       = google_storage_bucket.documents.name
}

output "storage_documents_bucket_url" {
  description = "Documents storage bucket URL"
  value       = "gs://${google_storage_bucket.documents.name}"
}

output "storage_recordings_bucket" {
  description = "Recordings storage bucket name"
  value       = google_storage_bucket.recordings.name
}

output "storage_recordings_bucket_url" {
  description = "Recordings storage bucket URL"
  value       = "gs://${google_storage_bucket.recordings.name}"
}

output "storage_exports_bucket" {
  description = "Exports storage bucket name"
  value       = google_storage_bucket.exports.name
}

output "storage_exports_bucket_url" {
  description = "Exports storage bucket URL"
  value       = "gs://${google_storage_bucket.exports.name}"
}

# Secret Manager Outputs
output "jwt_secret_name" {
  description = "JWT secret name in Secret Manager"
  value       = google_secret_manager_secret.jwt_secret.id
}

# Service Account Outputs
output "api_service_account" {
  description = "API service account email"
  value       = google_service_account.api.email
}

output "api_service_account_id" {
  description = "API service account ID"
  value       = google_service_account.api.unique_id
}

output "web_service_account" {
  description = "Web service account email"
  value       = google_service_account.web.email
}

output "web_service_account_id" {
  description = "Web service account ID"
  value       = google_service_account.web.unique_id
}

# Cloud Run Outputs
output "api_url" {
  description = "API Cloud Run service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "api_service_name" {
  description = "API Cloud Run service name"
  value       = google_cloud_run_service.api.name
}

output "web_url" {
  description = "Web Cloud Run service URL"
  value       = google_cloud_run_service.web.status[0].url
}

output "web_service_name" {
  description = "Web Cloud Run service name"
  value       = google_cloud_run_service.web.name
}

# Artifact Registry Outputs
output "artifact_registry_repository_url" {
  description = "Artifact Registry Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}

output "artifact_registry_repository_name" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.docker.repository_id
}

# Networking Outputs
output "vpc_network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "vpc_network_id" {
  description = "VPC network ID"
  value       = google_compute_network.main.id
}

output "vpc_subnetwork_name" {
  description = "VPC subnetwork name"
  value       = google_compute_subnetwork.main.name
}

output "vpc_subnetwork_id" {
  description = "VPC subnetwork ID"
  value       = google_compute_subnetwork.main.id
}

# Consolidated Environment Configuration
output "environment_config" {
  description = "Consolidated environment configuration"
  value = {
    environment = var.environment
    region      = var.region
    app_name    = var.app_name

    database = {
      host           = google_sql_database_instance.main.private_ip_address
      port           = 5432
      name           = google_sql_database.main.name
      user           = google_sql_user.app.name
      connection_name = google_sql_database_instance.main.connection_name
    }

    redis = {
      host = google_redis_instance.cache.host
      port = google_redis_instance.cache.port
    }

    storage = {
      documents = google_storage_bucket.documents.name
      recordings = google_storage_bucket.recordings.name
      exports   = google_storage_bucket.exports.name
    }

    services = {
      api_url = google_cloud_run_service.api.status[0].url
      web_url = google_cloud_run_service.web.status[0].url
    }

    artifact_registry = {
      repository_url = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
    }
  }
  sensitive = true
}

# Connection String for Application
output "application_database_url" {
  description = "Full database connection URL for application"
  value       = "postgresql://${google_sql_user.app.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.main.name}?sslmode=require"
  sensitive   = true
}

output "application_redis_url" {
  description = "Full Redis connection URL for application"
  value       = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
  sensitive   = true
}
