# Configure Terraform state backend in Google Cloud Storage
# This file is separate to allow flexible backend configuration per environment

# Uncomment and configure when using remote state storage
# terraform {
#   backend "gcs" {
#     bucket  = "ai-platform-terraform-state"
#     prefix  = "gcp/dev"
#   }
# }

# To use different state files per environment, run:
# terraform init -backend-config="bucket=ai-platform-terraform-state" -backend-config="prefix=gcp/dev"
# terraform init -backend-config="bucket=ai-platform-terraform-state" -backend-config="prefix=gcp/staging"
# terraform init -backend-config="bucket=ai-platform-terraform-state" -backend-config="prefix=gcp/production"

# Create GCS bucket for Terraform state (run this separately first)
resource "google_storage_bucket" "terraform_state" {
  name          = "ai-platform-terraform-state-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      num_newer_versions = 5
    }
    action {
      type = "Delete"
    }
  }

  labels = merge(
    local.labels,
    {
      purpose = "terraform-state"
    }
  )
}

# Enable versioning for state recovery
resource "google_storage_bucket_versioning" "terraform_state" {
  bucket = google_storage_bucket.terraform_state.id
  versioning_config {
    enabled = true
  }
}
