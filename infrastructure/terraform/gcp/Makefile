.PHONY: help init validate plan apply destroy fmt lint clean test

# Variables
ENVIRONMENT ?= dev
TFVARS_FILE = terraform.tfvars.$(ENVIRONMENT)
REGION ?= us-central1

help:
	@echo "GCP Terraform Makefile Commands"
	@echo ""
	@echo "Usage: make [target] ENVIRONMENT=[dev|staging|production]"
	@echo ""
	@echo "Targets:"
	@echo "  init              Initialize Terraform backend"
	@echo "  validate          Validate Terraform configuration"
	@echo "  fmt               Format Terraform files"
	@echo "  lint              Run terraform fmt and validate"
	@echo "  plan              Plan Terraform changes"
	@echo "  apply             Apply Terraform changes"
	@echo "  destroy           Destroy Terraform resources"
	@echo "  state-list        List Terraform state resources"
	@echo "  state-backup      Backup Terraform state"
	@echo "  state-pull        Pull Terraform state"
	@echo "  state-push        Push Terraform state"
	@echo "  output            Show Terraform outputs"
	@echo "  refresh           Refresh Terraform state"
	@echo "  test              Validate all terraform configurations"
	@echo "  clean             Remove Terraform files"
	@echo "  setup-gcp         Setup GCP project and service account"
	@echo "  enable-apis       Enable required GCP APIs"
	@echo "  build-images      Build and push Docker images"
	@echo "  deploy-full       Full deployment (plan + apply)"
	@echo "  get-urls          Get deployed service URLs"
	@echo "  logs-api          View API Cloud Run logs"
	@echo "  logs-web          View Web Cloud Run logs"
	@echo ""
	@echo "Examples:"
	@echo "  make plan ENVIRONMENT=dev"
	@echo "  make apply ENVIRONMENT=staging"
	@echo "  make destroy ENVIRONMENT=dev"

.check-env:
	@if [ ! -f "$(TFVARS_FILE)" ]; then \
		echo "Error: $(TFVARS_FILE) not found"; \
		exit 1; \
	fi

init: .check-env
	@echo "Initializing Terraform for $(ENVIRONMENT) environment..."
	terraform init -upgrade

validate: .check-env
	@echo "Validating Terraform configuration for $(ENVIRONMENT)..."
	terraform validate

fmt:
	@echo "Formatting Terraform files..."
	terraform fmt -recursive .

lint: fmt validate
	@echo "Linting complete"

plan: .check-env validate
	@echo "Planning Terraform changes for $(ENVIRONMENT) environment..."
	terraform plan -var-file="$(TFVARS_FILE)" -out="tfplan.$(ENVIRONMENT)"

apply: .check-env
	@echo "Applying Terraform changes for $(ENVIRONMENT) environment..."
	@if [ ! -f "tfplan.$(ENVIRONMENT)" ]; then \
		echo "Error: tfplan.$(ENVIRONMENT) not found. Run 'make plan ENVIRONMENT=$(ENVIRONMENT)' first"; \
		exit 1; \
	fi
	terraform apply tfplan.$(ENVIRONMENT)
	@rm -f tfplan.$(ENVIRONMENT)

destroy: .check-env
	@echo "WARNING: This will destroy all resources in $(ENVIRONMENT) environment"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		terraform destroy -var-file="$(TFVARS_FILE)"; \
	else \
		echo "Aborted"; \
	fi

state-list:
	@terraform state list

state-backup:
	@echo "Backing up Terraform state..."
	@mkdir -p .state-backups
	@terraform state pull > ".state-backups/terraform.state.backup.$(shell date +%Y%m%d_%H%M%S).json"
	@echo "State backed up to .state-backups/"

state-pull:
	@terraform state pull

state-push:
	@echo "Error: Use 'terraform state push <file>' directly"
	@exit 1

output:
	@terraform output

refresh:
	@echo "Refreshing Terraform state..."
	terraform refresh -var-file="$(TFVARS_FILE)"

test:
	@echo "Testing all Terraform configurations..."
	@for env in dev staging production; do \
		echo "Validating $$env..."; \
		terraform validate -var-file="terraform.tfvars.$$env" || exit 1; \
	done
	@echo "All configurations valid!"

clean:
	@echo "Cleaning Terraform files..."
	@rm -rf .terraform/
	@rm -f .terraform.lock.hcl
	@rm -f tfplan.*
	@echo "Cleaned"

setup-gcp:
	@echo "Setting up GCP project..."
	@if [ -z "$$PROJECT_ID" ]; then \
		echo "Error: PROJECT_ID environment variable not set"; \
		exit 1; \
	fi
	@gcloud projects create $$PROJECT_ID --name="AI Platform $(ENVIRONMENT)"
	@gcloud config set project $$PROJECT_ID
	@echo "GCP project created and set as default"

enable-apis:
	@echo "Enabling required GCP APIs..."
	@if [ -z "$$PROJECT_ID" ]; then \
		echo "Error: PROJECT_ID environment variable not set"; \
		exit 1; \
	fi
	@gcloud services enable \
		run.googleapis.com \
		cloudbuild.googleapis.com \
		cloudresourcemanager.googleapis.com \
		sqladmin.googleapis.com \
		redis.googleapis.com \
		storage-api.googleapis.com \
		secretmanager.googleapis.com \
		compute.googleapis.com \
		cloudscheduler.googleapis.com \
		artifactregistry.googleapis.com \
		--project=$$PROJECT_ID
	@echo "APIs enabled"

build-images:
	@echo "Building and pushing Docker images for $(ENVIRONMENT)..."
	@if [ -z "$$PROJECT_ID" ]; then \
		echo "Error: PROJECT_ID environment variable not set"; \
		exit 1; \
	fi
	@gcloud auth configure-docker $(REGION)-docker.pkg.dev
	@docker build -f ../../backend/Dockerfile -t $(REGION)-docker.pkg.dev/$$PROJECT_ID/ai-platform-$(ENVIRONMENT)-docker/api:latest ../../backend
	@docker push $(REGION)-docker.pkg.dev/$$PROJECT_ID/ai-platform-$(ENVIRONMENT)-docker/api:latest
	@docker build -f ../../frontend/Dockerfile -t $(REGION)-docker.pkg.dev/$$PROJECT_ID/ai-platform-$(ENVIRONMENT)-docker/web:latest ../../frontend
	@docker push $(REGION)-docker.pkg.dev/$$PROJECT_ID/ai-platform-$(ENVIRONMENT)-docker/web:latest
	@echo "Docker images pushed"

deploy-full: plan apply
	@echo "Deployment complete!"

get-urls:
	@echo "Service URLs for $(ENVIRONMENT) environment:"
	@echo "API URL: $$(terraform output -raw api_url)"
	@echo "Web URL: $$(terraform output -raw web_url)"

logs-api:
	@echo "Fetching API logs..."
	@gcloud logging read "resource.type=cloud_run_revision" --limit 50 --format=json | \
		jq '.[] | select(.resource.labels.service_name | contains("api")) | {time: .timestamp, message: .textPayload}' || \
		echo "No logs found or API not deployed"

logs-web:
	@echo "Fetching Web logs..."
	@gcloud logging read "resource.type=cloud_run_revision" --limit 50 --format=json | \
		jq '.[] | select(.resource.labels.service_name | contains("web")) | {time: .timestamp, message: .textPayload}' || \
		echo "No logs found or Web not deployed"

format: fmt

plan-all:
	@echo "Planning all environments..."
	@for env in dev staging production; do \
		echo "\n=== Planning $$env ==="; \
		$(MAKE) plan ENVIRONMENT=$$env; \
	done

show-plan:
	@if [ ! -f "tfplan.$(ENVIRONMENT)" ]; then \
		echo "Error: tfplan.$(ENVIRONMENT) not found"; \
		exit 1; \
	fi
	@terraform show tfplan.$(ENVIRONMENT)

# Development convenience targets
dev-init:
	$(MAKE) init ENVIRONMENT=dev

dev-plan:
	$(MAKE) plan ENVIRONMENT=dev

dev-apply:
	$(MAKE) apply ENVIRONMENT=dev

dev-destroy:
	$(MAKE) destroy ENVIRONMENT=dev

# Staging convenience targets
staging-init:
	$(MAKE) init ENVIRONMENT=staging

staging-plan:
	$(MAKE) plan ENVIRONMENT=staging

staging-apply:
	$(MAKE) apply ENVIRONMENT=staging

# Production convenience targets
prod-init:
	$(MAKE) init ENVIRONMENT=production

prod-plan:
	$(MAKE) plan ENVIRONMENT=production

prod-apply:
	$(MAKE) apply ENVIRONMENT=production
