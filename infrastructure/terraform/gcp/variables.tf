variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ai-platform"
}

variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}

variable "database_instance_type" {
  description = "Cloud SQL instance machine type"
  type        = string
  default     = "db-f1-micro"
}

variable "redis_memory_size" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD)"
  type        = string
  default     = "BASIC"
}

variable "api_memory" {
  description = "Cloud Run API memory allocation (Mi)"
  type        = number
  default     = 512
}

variable "api_cpu" {
  description = "Cloud Run API CPU allocation"
  type        = string
  default     = "1"
}

variable "api_max_instances" {
  description = "Cloud Run API max instances"
  type        = number
  default     = 10
}

variable "web_memory" {
  description = "Cloud Run Web memory allocation (Mi)"
  type        = number
  default     = 256
}

variable "web_cpu" {
  description = "Cloud Run Web CPU allocation"
  type        = string
  default     = "1"
}

variable "web_max_instances" {
  description = "Cloud Run Web max instances"
  type        = number
  default     = 5
}

variable "allowed_ingress" {
  description = "Cloud Run allowed ingress (ALLOW_ALL or ALLOW_INTERNAL_ONLY)"
  type        = string
  default     = "ALLOW_ALL"
}

variable "labels" {
  description = "Common labels for all resources"
  type        = map(string)
  default = {
    managed_by = "terraform"
  }
}

variable "enable_apis" {
  description = "GCP APIs to enable"
  type        = list(string)
  default = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "storage-api.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "cloudscheduler.googleapis.com",
  ]
}
