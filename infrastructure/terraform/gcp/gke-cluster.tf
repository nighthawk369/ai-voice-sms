# ============================================================
# GKE Cluster Configuration
# ============================================================

# GKE Cluster for Development/Staging/Production
resource "google_container_cluster" "primary" {
  name     = "${local.service_name}-gke-cluster"
  location = var.region

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Network Policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }

  # Logging and Monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
  }

  # Maintenance Window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Security settings
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Resource labels
  resource_labels = local.common_labels

  depends_on = [
    google_compute_network.main,
    google_compute_subnetwork.main
  ]
}

# Secondary IP ranges for cluster
resource "google_compute_subnetwork" "kubernetes" {
  name          = "${local.service_name}-k8s-secondary"
  ip_cidr_range = "10.1.0.0/16"
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.0.0.0/20"
  }
}

# ============================================================
# GKE Node Pools with Auto-scaling
# ============================================================

# Development Node Pool
resource "google_container_node_pool" "development" {
  name       = "${local.service_name}-dev-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.environment == "dev" ? 1 : 0

  autoscaling {
    min_node_count = var.environment == "dev" ? 1 : 0
    max_node_count = var.environment == "dev" ? 3 : 0
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = var.environment == "dev" ? true : false
    machine_type = var.environment == "dev" ? "e2-standard-2" : "n1-standard-2"

    disk_size_gb = 50
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    labels = merge(
      local.common_labels,
      {
        pool = "development"
      }
    )

    tags = ["gke-node", "${local.service_name}-dev"]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Shielded instance
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  depends_on = [google_container_cluster.primary]
}

# Staging Node Pool
resource "google_container_node_pool" "staging" {
  name       = "${local.service_name}-staging-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.environment == "staging" ? 2 : 0

  autoscaling {
    min_node_count = var.environment == "staging" ? 2 : 0
    max_node_count = var.environment == "staging" ? 5 : 0
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = false
    machine_type = var.environment == "staging" ? "n1-standard-2" : "n1-standard-4"

    disk_size_gb = 100
    disk_type    = "pd-ssd"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = merge(
      local.common_labels,
      {
        pool = "staging"
      }
    )

    tags = ["gke-node", "${local.service_name}-staging"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  depends_on = [google_container_cluster.primary]
}

# Production Node Pool
resource "google_container_node_pool" "production" {
  name       = "${local.service_name}-prod-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.environment == "production" ? 3 : 0

  autoscaling {
    min_node_count = var.environment == "production" ? 3 : 0
    max_node_count = var.environment == "production" ? 20 : 0
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = false
    machine_type = var.environment == "production" ? "n1-standard-4" : "n1-standard-8"

    disk_size_gb = 200
    disk_type    = "pd-ssd"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = merge(
      local.common_labels,
      {
        pool = "production"
      }
    )

    tags = ["gke-node", "${local.service_name}-prod"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    taint {
      key    = "production"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  }

  depends_on = [google_container_cluster.primary]
}

# ============================================================
# Outputs
# ============================================================

output "gke_cluster_name" {
  description = "GKE Cluster name"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "GKE Cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "gke_cluster_ca_certificate" {
  description = "GKE Cluster CA certificate"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "kubernetes_cluster_host" {
  description = "Kubernetes cluster host"
  value       = "https://${google_container_cluster.primary.endpoint}"
  sensitive   = true
}
