# ============================================================
# Cloud Run Services
# ============================================================

# API Service
resource "google_cloud_run_service" "api" {
  name     = "${local.service_name}-api"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.api.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/api:latest"

        resources {
          limits = {
            cpu    = var.api_cpu
            memory = "${var.api_memory}Mi"
          }
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.app.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.main.name}?sslmode=require"
        }

        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "GCS_BUCKET_DOCUMENTS"
          value = google_storage_bucket.documents.name
        }

        env {
          name  = "GCS_BUCKET_RECORDINGS"
          value = google_storage_bucket.recordings.name
        }

        env {
          name  = "GCS_BUCKET_EXPORTS"
          value = google_storage_bucket.exports.name
        }
      }

      timeout_seconds = 300
    }

    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
        "autoscaling.knative.dev/maxScale"       = var.api_max_instances
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis["run.googleapis.com"]]
}

# Allow unauthenticated access to API (configure in ingress settings)
resource "google_cloud_run_service_iam_member" "api_public" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Web Service (Frontend)
resource "google_cloud_run_service" "web" {
  name     = "${local.service_name}-web"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.web.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/web:latest"

        resources {
          limits = {
            cpu    = var.web_cpu
            memory = "${var.web_memory}Mi"
          }
        }

        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = google_cloud_run_service.api.status[0].url
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      }

      timeout_seconds = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = var.web_max_instances
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.required_apis["run.googleapis.com"]]
}

# Allow unauthenticated access to Web
resource "google_cloud_run_service_iam_member" "web_public" {
  service  = google_cloud_run_service.web.name
  location = google_cloud_run_service.web.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ============================================================
# Cloud Armor Security Policy (DDoS Protection)
# ============================================================

resource "google_compute_security_policy" "cloud_armor" {
  name = "${local.service_name}-cloud-armor"

  # Allow all by default
  rules {
    action   = "allow"
    priority = "65535"
    match {
      versioned_expr = "EXPR_V1"
      expr {
        expression = "*"
      }
    }
    description = "Default rule"
  }

  # Rate limit: 100 requests per minute per IP
  rules {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "EXPR_V1"
      expr {
        expression = "*"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"

      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }

      ban_duration_sec = 600
    }
    description = "Rate limit rule"
  }
}

# ============================================================
# Load Balancer (Cloud Load Balancing)
# ============================================================

resource "google_compute_backend_service" "api" {
  name            = "${local.service_name}-api-backend"
  protocol        = "HTTPS"
  security_policy = google_compute_security_policy.cloud_armor.id

  custom_request_headers {
    headers = [
      "X-Client-Region:{client_region}",
    ]
  }
}

resource "google_compute_backend_service" "web" {
  name            = "${local.service_name}-web-backend"
  protocol        = "HTTPS"
  security_policy = google_compute_security_policy.cloud_armor.id
}

# ============================================================
# Cloud Scheduler (for Cron Jobs)
# ============================================================

resource "google_cloud_scheduler_job" "database_backup" {
  name        = "${local.service_name}-backup-scheduler"
  description = "Daily database backup"
  schedule    = "0 3 * * *"  # 3 AM daily
  region      = var.region
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.api.status[0].url}/admin/backup"

    oidc_token {
      service_account_email = google_service_account.api.email
    }
  }
}

# ============================================================
# Monitoring & Alerts
# ============================================================

resource "google_monitoring_notification_channel" "email" {
  display_name = "${local.service_name} Email Alert"
  type         = "email"
  labels = {
    email_address = "alerts@example.com"  # Update with your email
  }
  enabled = true
}

resource "google_monitoring_alert_policy" "api_error_rate" {
  display_name = "${local.service_name} API Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 1%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metadata.user_labels.\"service\"=\"api\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.01
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_monitoring_alert_policy" "api_latency" {
  display_name = "${local.service_name} API Latency"
  combiner     = "OR"

  conditions {
    display_name = "P95 latency > 5s"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\" AND metadata.user_labels.\"service\"=\"api\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5000
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# ============================================================
# Outputs
# ============================================================

output "api_url" {
  description = "API service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "web_url" {
  description = "Web service URL"
  value       = google_cloud_run_service.web.status[0].url
}
