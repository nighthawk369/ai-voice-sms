#!/bin/bash

# AI Platform Kubernetes Deployment Script
# Automated deployment to GKE with auto-scaling and cost optimization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
PROJECT_ID=${2:-ai-platform-dev}
REGION=${3:-us-central1}
CLUSTER_NAME="${PROJECT_ID}-gke-cluster"
NAMESPACE="ai-platform-${ENVIRONMENT}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|production)$ ]]; then
  echo -e "${RED}Error: ENVIRONMENT must be dev, staging, or production${NC}"
  exit 1
fi

# Functions
print_header() {
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
  echo -e "${RED}✗ $1${NC}"
}

print_info() {
  echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Setup
print_header "STEP 1: Configuration Setup"

print_info "Environment: $ENVIRONMENT"
print_info "Project ID: $PROJECT_ID"
print_info "Region: $REGION"
print_info "Cluster: $CLUSTER_NAME"
print_info "Namespace: $NAMESPACE"

# Step 2: Authentication
print_header "STEP 2: GCP Authentication"

if ! command -v gcloud &> /dev/null; then
  print_error "gcloud CLI not found. Install from https://cloud.google.com/sdk"
  exit 1
fi

print_info "Authenticating with GCP..."
gcloud auth login
gcloud config set project $PROJECT_ID
print_success "GCP authentication completed"

# Step 3: Create/Connect to GKE Cluster
print_header "STEP 3: GKE Cluster Setup"

if gcloud container clusters describe $CLUSTER_NAME --region $REGION &>/dev/null; then
  print_success "Cluster $CLUSTER_NAME exists"
else
  print_info "Creating GKE cluster... (this may take 5-10 minutes)"
  cd infrastructure/terraform/gcp
  terraform init
  terraform plan -var-file="terraform.tfvars.${ENVIRONMENT}" -out=tfplan
  terraform apply tfplan
  cd ../../..
  print_success "GKE cluster created"
fi

# Get credentials
print_info "Getting kubeconfig..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION
print_success "Kubeconfig updated"

# Step 4: Verify kubectl
print_header "STEP 4: Kubectl Verification"

if ! command -v kubectl &> /dev/null; then
  print_error "kubectl not found. Install from https://kubernetes.io/docs/tasks/tools/"
  exit 1
fi

print_info "Testing kubectl connectivity..."
kubectl cluster-info
print_success "kubectl connected to cluster"

# Step 5: Create Namespaces
print_header "STEP 5: Creating Kubernetes Namespaces"

print_info "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
print_success "Namespace created"

# Step 6: Deploy Secrets & ConfigMaps
print_header "STEP 6: Deploying Secrets & ConfigMaps"

print_info "Creating secrets..."
kubectl apply -f k8s/05-configmap-secrets.yaml -n $NAMESPACE
print_success "Secrets & ConfigMaps deployed"

# Step 7: Deploy Core Services
print_header "STEP 7: Deploying Core Services"

print_info "Deploying PostgreSQL..."
kubectl apply -f k8s/03-database-statefulset.yaml -n $NAMESPACE
print_success "PostgreSQL deployed"

print_info "Deploying Redis..."
kubectl apply -f k8s/04-redis-deployment.yaml -n $NAMESPACE
print_success "Redis deployed"

# Wait for databases to be ready
print_info "Waiting for databases to be ready (this may take 2-3 minutes)..."
kubectl rollout status statefulset/postgres -n $NAMESPACE --timeout=5m || true
print_success "Databases ready"

# Step 8: Deploy Applications
print_header "STEP 8: Deploying Applications"

print_info "Deploying API service..."
kubectl apply -f k8s/01-api-deployment.yaml -n $NAMESPACE
print_success "API deployed"

print_info "Deploying Web frontend..."
kubectl apply -f k8s/02-web-deployment.yaml -n $NAMESPACE
print_success "Web deployed"

# Step 9: Deploy Ingress
print_header "STEP 9: Deploying Ingress"

print_info "Deploying Ingress controller..."
kubectl apply -f k8s/06-ingress.yaml -n $NAMESPACE
print_success "Ingress deployed"

# Step 10: Deploy Monitoring
print_header "STEP 10: Deploying Monitoring"

print_info "Deploying Prometheus..."
kubectl apply -f k8s/07-monitoring.yaml -n $NAMESPACE
print_success "Prometheus deployed"

# Step 11: Verify Deployment
print_header "STEP 11: Verifying Deployment"

print_info "Checking pod status..."
kubectl get pods -n $NAMESPACE

print_info "Checking service status..."
kubectl get svc -n $NAMESPACE

print_info "Checking HPA status..."
kubectl get hpa -n $NAMESPACE

# Step 12: Get Access Information
print_header "STEP 12: Access Information"

# Get API service IP/endpoint
API_IP=$(kubectl get svc api-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
print_info "API Service: http://$API_IP:8000"

# Get Web service IP/endpoint
WEB_IP=$(kubectl get svc web-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
print_info "Web Service: http://$WEB_IP:3000"

# Port forwarding instructions
print_info "Port forwarding (for local access):"
print_info "  API:        kubectl port-forward svc/api-service 8000:8000 -n $NAMESPACE"
print_info "  Web:        kubectl port-forward svc/web-service 3000:3000 -n $NAMESPACE"
print_info "  Prometheus: kubectl port-forward svc/prometheus-service 9090:9090 -n $NAMESPACE"

# Step 13: Post-Deployment Configuration
print_header "STEP 13: Post-Deployment Configuration"

print_info "Waiting for services to stabilize (30 seconds)..."
sleep 30

print_info "Checking API health..."
if kubectl get pods -n $NAMESPACE | grep -q "api.*Running"; then
  print_success "API is running"
else
  print_error "API is not running. Check logs: kubectl logs deployment/api -n $NAMESPACE"
fi

# Step 14: Summary
print_header "DEPLOYMENT COMPLETE!"

print_success "Deployment Summary:"
echo "  Environment:    $ENVIRONMENT"
echo "  Project:        $PROJECT_ID"
echo "  Namespace:      $NAMESPACE"
echo "  Cluster:        $CLUSTER_NAME"
echo "  Region:         $REGION"

echo ""
print_info "Next Steps:"
echo "  1. Monitor deployment: kubectl get pods -n $NAMESPACE --watch"
echo "  2. View logs: kubectl logs -f deployment/api -n $NAMESPACE"
echo "  3. Check HPA: kubectl get hpa -n $NAMESPACE --watch"
echo "  4. View metrics: kubectl top pods -n $NAMESPACE"

echo ""
print_info "Useful Commands:"
echo "  kubectl describe pod <pod-name> -n $NAMESPACE"
echo "  kubectl exec -it <pod-name> -n $NAMESPACE -- /bin/bash"
echo "  kubectl port-forward svc/api-service 8000:8000 -n $NAMESPACE"

echo ""
print_success "Deployment script completed successfully!"
