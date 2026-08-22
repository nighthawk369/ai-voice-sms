# GCP Terraform Infrastructure

This directory contains Terraform configuration for deploying the AI Platform to Google Cloud Platform.

## Directory Structure

```
gcp/
├── README.md                      # This file
├── DEPLOYMENT_GUIDE.md           # Comprehensive deployment guide
├── Makefile                      # Convenient make targets
├── main.tf                       # Core infrastructure (VPC, Cloud SQL, Redis, Storage, Secrets, IAM)
├── cloud_run.tf                  # Cloud Run services (API, Web), Load Balancing, Monitoring, Scheduler
├── backend.tf                    # Terraform state backend configuration
├── provider.tf                   # Provider configuration and API enablement
├── variables.tf                  # Variable definitions
├── outputs.tf                    # Output definitions
├── locals.tf                     # Local values for DRY configuration
├── terraform.tfvars.dev          # Dev environment variables
├── terraform.tfvars.staging      # Staging environment variables
└── terraform.tfvars.production   # Production environment variables
```

## File Descriptions

### Core Configuration Files

- **main.tf**: Contains the core infrastructure including:
  - VPC and networking (Virtual Network, Subnet)
  - Cloud SQL PostgreSQL database with automatic backups
  - Cloud Memorystore Redis cache
  - Cloud Storage buckets (documents, recordings, exports)
  - Secret Manager secrets (database password, JWT secret)
  - Service accounts and IAM roles
  - Artifact Registry for Docker images

- **cloud_run.tf**: Contains Cloud Run services and related resources:
  - Cloud Run service for API
  - Cloud Run service for Web frontend
  - Cloud Armor security policies (DDoS protection, rate limiting)
  - Load balancer backend services
  - Cloud Scheduler for automated tasks
  - Cloud Monitoring alerts and notification channels

- **backend.tf**: Terraform state management:
  - Configuration for remote state storage in GCS
  - GCS bucket for Terraform state with versioning

- **provider.tf**: GCP provider setup:
  - Google provider configuration
  - Required provider versions
  - API enablement resources
  - Terraform Cloud/Enterprise configuration

### Configuration Files

- **variables.tf**: Defines all input variables:
  - Project and region settings
  - Database configuration
  - Redis configuration
  - Cloud Run resource allocation
  - Security and ingress settings

- **locals.tf**: Computed values:
  - Service naming conventions
  - Common labels
  - Environment-specific configurations
  - Resource names
  - Feature flags

- **outputs.tf**: Exported values:
  - Database connection details
  - Redis connection details
  - Cloud Run service URLs
  - Service account emails
  - Cloud Storage bucket names

### Environment Files

- **terraform.tfvars.dev**: Development environment configuration
- **terraform.tfvars.staging**: Staging environment configuration
- **terraform.tfvars.production**: Production environment configuration

Each environment file specifies:
- GCP project ID
- Database instance type
- Redis memory allocation
- Cloud Run resource limits
- Service scaling settings

## Quick Start

### 1. Prerequisites

```bash
# Install Terraform
brew install terraform  # macOS
# or visit https://www.terraform.io/downloads.html

# Install gcloud CLI
brew install google-cloud-sdk  # macOS
# or visit https://cloud.google.com/sdk/docs/install

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login
```

### 2. Initialize Terraform

```bash
cd infrastructure/terraform/gcp

# Initialize for development environment
make dev-init

# Or for other environments
make staging-init
make prod-init
```

### 3. Plan Deployment

```bash
# Plan dev deployment
make dev-plan

# Or use the Makefile with environment variable
make plan ENVIRONMENT=dev
```

### 4. Apply Configuration

```bash
# Apply dev deployment
make dev-apply

# Or for staging/production
make staging-apply
make prod-apply
```

### 5. View Outputs

```bash
# Get all service URLs and configuration
make output

# Or specific values
terraform output api_url
terraform output web_url
```

## Common Commands

### Development Workflow

```bash
# Format code
make fmt

# Validate configuration
make lint

# Plan changes
make plan ENVIRONMENT=dev

# Apply changes
make apply ENVIRONMENT=dev

# Destroy environment
make destroy ENVIRONMENT=dev
```

### State Management

```bash
# List resources in state
make state-list

# Backup state
make state-backup

# Get all outputs
make output
```

### Monitoring and Logs

```bash
# Get API and Web service URLs
make get-urls

# View API logs
make logs-api

# View Web logs
make logs-web
```

### Deployment

```bash
# Full deployment (plan + apply)
make deploy-full ENVIRONMENT=staging

# Build and push Docker images
make build-images

# Setup GCP project and APIs
PROJECT_ID=my-project make setup-gcp
PROJECT_ID=my-project make enable-apis
```

## Environment Variables

### Required for GCP Operations

```bash
# GCP project ID (required for setup-gcp, enable-apis, build-images)
export PROJECT_ID=ai-platform-dev

# Region (optional, default: us-central1)
export REGION=us-central1

# Terraform authentication
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Terraform Variables

All variables are defined in `variables.tf`. Key variables by environment:

**Development:**
- Database: db-f1-micro
- Redis: 1GB BASIC
- API: 512Mi memory, 1 CPU, 5 max instances
- Web: 256Mi memory, 1 CPU, 3 max instances

**Staging:**
- Database: db-n1-standard-1
- Redis: 2GB STANDARD
- API: 1024Mi memory, 2 CPU, 10 max instances
- Web: 512Mi memory, 2 CPU, 8 max instances

**Production:**
- Database: db-n1-standard-2
- Redis: 4GB STANDARD
- API: 2048Mi memory, 4 CPU, 50 max instances
- Web: 1024Mi memory, 2 CPU, 30 max instances

## Resource Overview

### Compute

- **Cloud Run**: Serverless container deployment for API and Web services
- **Cloud Scheduler**: Scheduled jobs (daily database backups)

### Data Storage

- **Cloud SQL**: PostgreSQL managed database
  - Automatic backups in production
  - Point-in-time recovery
  - Query insights for performance monitoring

- **Cloud Memorystore**: Redis for caching and task queues
  - Automatic failover in STANDARD tier
  - Integrated VPC for private connectivity

- **Cloud Storage**: Object storage
  - Documents bucket (90-day retention)
  - Recordings bucket (30-day retention)
  - Exports bucket (7-day retention)

### Security

- **Secret Manager**: Stores sensitive data
  - Database password
  - JWT secret key

- **Service Accounts**: Identity and access management
  - Dedicated service accounts for API and Web services
  - Minimal IAM permissions per service

- **Cloud Armor**: DDoS protection and rate limiting
  - Rate limit: 100 requests/minute/IP
  - 10-minute ban for exceeding limit

### Networking

- **VPC**: Custom Virtual Private Cloud
- **Subnet**: Private subnet for resources
- **Private Service Access**: Secure connection to Cloud SQL and Redis
- **Load Balancer**: Traffic routing and SSL termination

### Monitoring

- **Cloud Monitoring**: Metrics and alerting
  - Error rate > 1% alerts
  - P95 latency > 5 seconds alerts
  - Email notifications

- **Cloud Logging**: Centralized logging for all services

## Deployment Workflow

### Development Deployment

```bash
# 1. Plan development deployment
make plan ENVIRONMENT=dev

# 2. Review the plan output carefully

# 3. Apply changes
make apply ENVIRONMENT=dev

# 4. Get service URLs
make get-urls
```

### Staging Deployment

```bash
# 1. Plan staging deployment
make plan ENVIRONMENT=staging

# 2. Review with team before proceeding

# 3. Apply changes
make apply ENVIRONMENT=staging

# 4. Run smoke tests
curl $(terraform output -raw api_url)/health/live
curl $(terraform output -raw web_url)
```

### Production Deployment

```bash
# 1. Create state backup
make state-backup

# 2. Plan production deployment
make plan ENVIRONMENT=production

# 3. Team review and approval required

# 4. Apply changes
make apply ENVIRONMENT=production

# 5. Verify deployment
curl $(terraform output -raw api_url)/health/live
```

## Scaling

### Manual Scaling

Modify `terraform.tfvars` files:

```hcl
# Increase API Cloud Run instances
api_max_instances = 100

# Increase database size
database_instance_type = "db-n1-standard-4"

# Increase Redis memory
redis_memory_size = 8
```

Then run:
```bash
make plan ENVIRONMENT=production
make apply ENVIRONMENT=production
```

### Automatic Scaling

Cloud Run automatically scales based on traffic. Configure via variables:
- `api_max_instances`: Maximum API service replicas
- `web_max_instances`: Maximum Web service replicas

## Cost Optimization

1. **Development**: Use smallest instance types (micro, 1GB Redis)
2. **Staging**: Use standard instances for realistic testing
3. **Production**: Right-size based on monitoring data
4. **Storage**: Implement lifecycle rules (already configured)
5. **Compute**: Use Cloud Run's per-request billing

## Disaster Recovery

### Automated Backups

- Cloud SQL: Daily backups at 3 AM UTC (retained 30 days in production)
- Cloud Storage: Versioning enabled for production
- Terraform State: Versioned in GCS bucket

### Recovery Procedures

```bash
# Restore from backup
gcloud sql backups restore BACKUP_ID --instance=INSTANCE_NAME

# Restore from GCS version
gcloud storage objects restore gs://bucket/object --generation=GENERATION

# Restore Terraform state
terraform state pull < .state-backups/terraform.state.backup.TIMESTAMP.json
```

## Troubleshooting

### Common Issues

**Terraform plan fails with permission errors:**
```bash
gcloud auth login
gcloud auth application-default login
```

**Cloud SQL connection fails:**
```bash
# Verify Private Service Access connection
gcloud compute networks peerings list

# Check service account has cloudsql.client role
gcloud projects get-iam-policy PROJECT_ID
```

**Cloud Run deployment fails:**
```bash
# Check service account has storage.objectAdmin role
gcloud projects get-iam-policy PROJECT_ID

# View Cloud Build logs
gcloud builds log --stream BUILD_ID
```

**Terraform state lock:**
```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

## CI/CD Integration

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for GitHub Actions workflow configuration.

## References

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Google Cloud Memorystore Documentation](https://cloud.google.com/memorystore/docs)

## Support

For issues or questions:
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting
2. Review Terraform logs: `TF_LOG=DEBUG terraform plan`
3. Check GCP Cloud Console for resource status
4. Review application logs: `make logs-api` or `make logs-web`
