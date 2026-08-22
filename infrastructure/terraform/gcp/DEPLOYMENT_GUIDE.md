# GCP Deployment Guide

This guide provides step-by-step instructions for deploying the AI Platform to Google Cloud Platform using Terraform.

## Prerequisites

1. **Google Cloud Account**: Create a GCP project
2. **Terraform**: Install Terraform 1.0+ ([download](https://www.terraform.io/downloads.html))
3. **gcloud CLI**: Install Google Cloud CLI ([setup guide](https://cloud.google.com/sdk/docs/install))
4. **Docker**: For building and pushing container images
5. **Service Account**: Create a GCP service account with appropriate permissions

## Initial Setup

### 1. Create GCP Projects

```bash
# Create dev project
gcloud projects create ai-platform-dev --name="AI Platform Dev"

# Create staging project
gcloud projects create ai-platform-staging --name="AI Platform Staging"

# Create production project
gcloud projects create ai-platform-prod --name="AI Platform Production"

# Set the default project
gcloud config set project ai-platform-dev
```

### 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Grant Editor role (for development; use more restrictive roles in production)
gcloud projects add-iam-policy-binding ai-platform-dev \
  --member="serviceAccount:terraform-sa@ai-platform-dev.iam.gserviceaccount.com" \
  --role="roles/editor"

# Create key file
gcloud iam service-accounts keys create terraform-key.json \
  --iam-account=terraform-sa@ai-platform-dev.iam.gserviceaccount.com
```

### 3. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  cloudresourcemanager.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com
```

### 4. Authenticate Terraform

```bash
# Set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/terraform-key.json

# Verify authentication
gcloud auth application-default print-access-token
```

## Deployment Steps

### 1. Prepare Container Images

Build and push Docker images to Artifact Registry:

```bash
# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build API image
docker build -f backend/Dockerfile -t us-central1-docker.pkg.dev/ai-platform-dev/ai-platform-dev-docker/api:latest ./backend
docker push us-central1-docker.pkg.dev/ai-platform-dev/ai-platform-dev-docker/api:latest

# Build Web image
docker build -f frontend/Dockerfile -t us-central1-docker.pkg.dev/ai-platform-dev/ai-platform-dev-docker/web:latest ./frontend
docker push us-central1-docker.pkg.dev/ai-platform-dev/ai-platform-dev-docker/web:latest
```

### 2. Initialize Terraform

```bash
cd infrastructure/terraform/gcp

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format configuration
terraform fmt -recursive
```

### 3. Plan Deployment

```bash
# For development
terraform plan \
  -var-file=terraform.tfvars.dev \
  -out=tfplan.dev

# For staging
terraform plan \
  -var-file=terraform.tfvars.staging \
  -out=tfplan.staging

# For production
terraform plan \
  -var-file=terraform.tfvars.production \
  -out=tfplan.prod
```

### 4. Apply Terraform Configuration

```bash
# For development
terraform apply tfplan.dev

# For staging
terraform apply tfplan.staging

# For production
terraform apply tfplan.prod
```

### 5. Retrieve Outputs

```bash
# View all outputs
terraform output

# Get specific output
terraform output database_host
terraform output redis_host
terraform output api_url
terraform output web_url
```

### 6. Configure Database

```bash
# Connect to database and run migrations
export PGPASSWORD=$(gcloud secrets versions access latest --secret="${app_name}-db-password")
export DB_HOST=$(terraform output -raw database_host)

# Run Alembic migrations
cd ../../..
alembic upgrade head
```

### 7. Deploy Secrets

The Terraform configuration automatically creates secrets in Secret Manager. Verify they are set:

```bash
# View secret names
gcloud secrets list

# Access secret value
gcloud secrets versions access latest --secret="${app_name}-db-password"
```

## Environment-Specific Workflows

### Development Deployment

```bash
# 1. Verify dev config
terraform plan -var-file=terraform.tfvars.dev -out=tfplan.dev

# 2. Apply changes
terraform apply tfplan.dev

# 3. Get API URL
terraform output api_url

# 4. Test API
curl $(terraform output -raw api_url)/health/live
```

### Staging Deployment

```bash
# 1. Plan staging deployment
terraform plan -var-file=terraform.tfvars.staging -out=tfplan.staging

# 2. Review output carefully before applying
terraform show tfplan.staging

# 3. Apply changes
terraform apply tfplan.staging

# 4. Run smoke tests
# Add your smoke test suite here
```

### Production Deployment

```bash
# 1. Plan production deployment
terraform plan -var-file=terraform.tfvars.production -out=tfplan.prod

# 2. Review output with team before applying
terraform show tfplan.prod

# 3. Create backup of current state
terraform state pull > terraform.state.backup.$(date +%Y%m%d_%H%M%S).json

# 4. Apply changes
terraform apply tfplan.prod

# 5. Verify deployment
curl $(terraform output -raw api_url)/health/live
curl $(terraform output -raw web_url)
```

## Managing State

### Backup State

```bash
# Manual backup
terraform state pull > terraform.state.backup.json

# Push state
terraform state push terraform.state.backup.json
```

### Remove Resource from State

```bash
# Remove without destroying
terraform state rm 'resource.type.name'
```

### Import Existing Resources

```bash
# Import existing Cloud Run service
terraform import google_cloud_run_service.api projects/PROJECT_ID/locations/REGION/services/SERVICE_NAME
```

## Monitoring and Debugging

### View Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${app_name}-api" --limit 50

# View last 10 deployments
gcloud run revisions list --service=${app_name}-api --region=us-central1
```

### Check Resource Status

```bash
# Database status
gcloud sql instances describe ${app_name}-db-${random_suffix}

# Redis status
gcloud redis instances describe ${app_name}-redis --region=us-central1

# Cloud Run services
gcloud run services list --region=us-central1
```

### Performance Monitoring

```bash
# View Cloud Run metrics
gcloud monitoring time-series list --filter='metric.type="run.googleapis.com/request_count"'

# View error rate
gcloud monitoring time-series list --filter='metric.type="run.googleapis.com/request_latencies"'
```

## Troubleshooting

### Common Issues

#### 1. Terraform State Lock

```bash
# Force unlock (use with caution)
terraform force-unlock LOCK_ID
```

#### 2. Database Connection Issues

```bash
# Check Cloud SQL proxy connectivity
cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME

# Verify network connectivity
gcloud compute ssh INSTANCE_NAME --zone=ZONE -- "nc -zv DATABASE_HOST 5432"
```

#### 3. Cloud Run Deployment Fails

```bash
# Check service account permissions
gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"

# View build logs
gcloud builds log --stream BUILD_ID
```

#### 4. Redis Connection Issues

```bash
# Check Redis instance status
gcloud redis instances describe INSTANCE_NAME --region=REGION

# View Redis events
gcloud events list --filter="resource:redis/instances/INSTANCE_NAME"
```

## Cleanup

### Destroy Resources

```bash
# Destroy dev environment
terraform destroy -var-file=terraform.tfvars.dev

# Destroy staging environment
terraform destroy -var-file=terraform.tfvars.staging

# Destroy production environment (requires extra confirmation)
terraform destroy -var-file=terraform.tfvars.production
```

### Clean Up Manually Created Resources

```bash
# Delete service account key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=terraform-sa@ai-platform-dev.iam.gserviceaccount.com

# Delete service account
gcloud iam service-accounts delete terraform-sa@ai-platform-dev.iam.gserviceaccount.com

# Delete projects (if needed)
gcloud projects delete ai-platform-dev
```

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/terraform-deploy.yml`:

```yaml
name: Terraform Deploy

on:
  push:
    branches: [main]
    paths:
      - 'infrastructure/terraform/gcp/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.0

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_TERRAFORM_KEY }}

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/terraform/gcp

      - name: Terraform Plan
        run: terraform plan -var-file=terraform.tfvars.dev -out=tfplan
        working-directory: infrastructure/terraform/gcp

      - name: Terraform Apply
        run: terraform apply tfplan
        working-directory: infrastructure/terraform/gcp
```

## Best Practices

1. **State Management**: Store Terraform state in a remote backend (Cloud Storage)
2. **Version Control**: Never commit sensitive files (.tfstate, terraform.tfvars with secrets)
3. **Code Review**: Always review `terraform plan` output before applying changes
4. **Tagging**: Use consistent labels and tags for resource management
5. **Monitoring**: Set up Cloud Monitoring alerts for key metrics
6. **Backups**: Regular database backups with automatic retention
7. **Disaster Recovery**: Document and test recovery procedures
8. **Access Control**: Use service accounts with minimal required permissions

## Next Steps

1. Configure domain and SSL certificates
2. Set up CDN for static assets
3. Configure custom domains for API and web services
4. Implement detailed monitoring and alerting
5. Set up automated backups and disaster recovery
6. Configure CI/CD pipeline for deployments
