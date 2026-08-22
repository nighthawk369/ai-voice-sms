# Kubernetes Deployment Guide - AI Platform

## Overview

Complete Kubernetes setup for AI Platform with automatic scaling, cost optimization, and production-grade configurations. Supports development, staging, and production environments with optimized resource allocation based on actual usage.

## Architecture

```
┌─────────────────────────────────────────────┐
│         Ingress Controller (Nginx)          │
│  Rate Limiting | SSL/TLS | CORS             │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    ┌────▼────┐     ┌────▼────┐
    │   API   │     │   Web    │
    │ Pods(5) │     │ Pods(5)  │
    │ HPA: 50 │     │ HPA: 30  │
    └────┬────┘     └────┬────┘
         │               │
         └───────┬───────┘
                 │
        ┌────────┼────────┐
        │        │        │
   ┌────▼──┐ ┌──▼────┐ ┌─▼────┐
   │  API  │ │ Redis │ │  DB  │
   │ Store │ │Cache  │ │(SST) │
   └───────┘ └───────┘ └──────┘
```

## Directory Structure

```
k8s/
├── 00-namespaces.yaml          # Namespaces & network policies
├── 01-api-deployment.yaml      # API with HPA
├── 02-web-deployment.yaml      # Frontend with HPA
├── 03-database-statefulset.yaml # PostgreSQL
├── 04-redis-deployment.yaml    # Redis cache
├── 05-configmap-secrets.yaml   # Secrets & config
├── 06-ingress.yaml             # Ingress & network policies
├── 07-monitoring.yaml          # Prometheus & Alerting
├── helm/
│   ├── Chart.yaml              # Helm chart metadata
│   ├── values-dev.yaml         # Dev environment values
│   ├── values-staging.yaml     # Staging environment values
│   └── values-production.yaml  # Production environment values
└── KUBERNETES_GUIDE.md         # This file
```

## Key Features

### Auto-Scaling

#### Horizontal Pod Autoscaling (HPA)
- **API Service**: 2-10 replicas (dev), 3-15 (staging), 5-50 (production)
- **Web Service**: 2-8 replicas (dev), 3-10 (staging), 5-30 (production)
- **Metrics**: CPU (50%), Memory (70%), Custom metrics
- **Behavior**: Aggressive scale-up (30s), Conservative scale-down (5m)

#### Vertical Pod Autoscaling (VPA)
- Recommends optimal CPU/memory based on actual usage
- Optional: Can automatically adjust resource requests

### Cost Optimization

**Development**
- Preemptible nodes (90% cheaper)
- Single node pool
- Minimal replicas (2 min)
- Total: ~$30-50/month

**Staging**
- Standard nodes
- 2-5 nodes with auto-scaling
- Moderate replicas
- Total: ~$150-250/month

**Production**
- Regional nodes with auto-repair/upgrade
- 3-20 nodes with auto-scaling
- High availability replicas
- Total: ~$400-700/month

### Resource Limits

```
Environment   | API CPU/Mem      | Web CPU/Mem     | DB CPU/Mem
──────────────┼──────────────────┼─────────────────┼────────────
Development   | 200-500m/256-512Mi | 100-250m/128-256Mi | 250-500m
Staging       | 500m-1/512Mi-1Gi  | 250-500m/256-512Mi | 500m-1
Production    | 1-2/1-2Gi        | 500m-1/512Mi-1Gi   | 2-4/2-4Gi
```

## Quick Start

### Prerequisites

```bash
# Install kubectl
brew install kubectl

# Install helm
brew install helm

# Install gcloud CLI
brew install google-cloud-sdk

# Install Prometheus Operator (optional)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### Deploy to GKE

```bash
# 1. Create GKE cluster (via Terraform)
cd infrastructure/terraform/gcp
terraform apply -var-file=terraform.tfvars.dev

# 2. Get kubeconfig
gcloud container clusters get-credentials ai-platform-dev-gke-cluster --region us-central1

# 3. Create namespaces
kubectl apply -f k8s/00-namespaces.yaml

# 4. Deploy applications
kubectl apply -f k8s/01-api-deployment.yaml
kubectl apply -f k8s/02-web-deployment.yaml
kubectl apply -f k8s/03-database-statefulset.yaml
kubectl apply -f k8s/04-redis-deployment.yaml
kubectl apply -f k8s/05-configmap-secrets.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-monitoring.yaml
```

### Or Deploy via Helm

```bash
# Development
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-dev.yaml \
  -n ai-platform-dev

# Staging
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-staging.yaml \
  -n ai-platform-staging

# Production
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-production.yaml \
  -n ai-platform-production
```

## Deployment Commands

### Check Deployment Status

```bash
# Get all resources
kubectl get all -n ai-platform-dev

# Watch deployments
kubectl rollout status deployment/api -n ai-platform-dev
kubectl rollout status deployment/web -n ai-platform-dev

# View pods
kubectl get pods -n ai-platform-dev -o wide

# View HPA status
kubectl get hpa -n ai-platform-dev
```

### Monitor Auto-Scaling

```bash
# Watch HPA in real-time
kubectl get hpa api-hpa -n ai-platform-dev --watch

# View HPA events
kubectl describe hpa api-hpa -n ai-platform-dev

# View metrics
kubectl top nodes
kubectl top pods -n ai-platform-dev
```

### View Logs

```bash
# API logs
kubectl logs -f deployment/api -n ai-platform-dev

# Web logs
kubectl logs -f deployment/web -n ai-platform-dev

# Database logs
kubectl logs -f statefulset/postgres -n ai-platform-dev
```

### Access Services

```bash
# Port forward to API
kubectl port-forward svc/api-service 8000:8000 -n ai-platform-dev

# Port forward to Web
kubectl port-forward svc/web-service 3000:3000 -n ai-platform-dev

# Port forward to Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ai-platform-dev
```

## Auto-Scaling Behavior

### CPU-Based Scaling

```
CPU Usage    | Target    | Action
─────────────┼───────────┼─────────────────────
< 30%        | Scale down by 50%/min
30-50%       | Hold current
50-70%       | Scale up by 100%/30s
> 70%        | Scale up by 100%/30s + alert
```

### Memory-Based Scaling

```
Memory Usage | Target    | Action
─────────────┼───────────┼─────────────────────
< 50%        | Scale down by 50%/min
50-70%       | Hold current
70-85%       | Scale up by 100%/30s
> 85%        | Scale up + alert
```

## Cost Optimization Strategies

### 1. Preemptible Nodes (Dev)
- 90% cost reduction for dev environments
- Suitable for non-critical workloads
- Auto-replacement on interruption

### 2. Cluster Auto-Scaling
- Automatically adjust node count
- Min 1 node (dev), 2 (staging), 3 (production)
- Max 3 nodes (dev), 5 (staging), 20 (production)

### 3. Pod Auto-Scaling
- Scale pods based on actual demand
- Conservative scale-down to save costs
- Aggressive scale-up for performance

### 4. Resource Requests/Limits
- Accurate requests prevent over-provisioning
- Limits prevent resource runaway
- Bin-packing improves node utilization

### 5. Scheduled Scaling (Optional)
```yaml
# Scale down during off-hours
schedule: "0 22 * * *"  # 10 PM
replicas: 1

# Scale up during peak hours
schedule: "0 7 * * 1-5" # 7 AM weekdays
replicas: 5
```

## Monitoring & Observability

### Prometheus Metrics

```yaml
# Pod metrics
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- http_requests_total
- http_request_duration_seconds

# Node metrics
- node_cpu_seconds_total
- node_memory_MemAvailable_bytes
- node_disk_io_time_seconds_total
```

### Alert Rules

```yaml
HighErrorRate:     error_rate > 5% for 5 min
HighLatency:       P95 latency > 2 sec
HighMemoryUsage:   memory > 85% of limit
HighCPUUsage:      CPU > 80% of limit
PodRestarting:     restarts > 0.1/min
APIUnavailable:    pod down for > 2 min
DatabasePoolExhausted: connections >= 90
```

## Database Considerations

### PostgreSQL StatefulSet
- Persistent storage via PVC
- Health checks (liveness & readiness)
- Single replica (no HA) for cost savings
- Environment-specific storage:
  - Dev: 20 Gi pd-standard
  - Staging: 50 Gi pd-ssd
  - Production: 200 Gi pd-ssd

### Backup Strategy
- Automated daily backups at 2 AM UTC
- 30-day retention in production
- Point-in-time recovery enabled

## Security Considerations

### Network Policies
- Deny-all by default
- Explicit allow rules per service
- Egress to DNS only (for external APIs)

### Pod Security
- Non-root user (1000)
- Read-only root filesystem
- No privilege escalation
- Dropped capabilities

### Secrets Management
- Kubernetes Secrets for development
- External Secrets Operator for production
- Sealed Secrets or Vault for sensitive data

### RBAC
- Service accounts per component
- Minimal permissions per role
- No cluster-admin roles

## Troubleshooting

### Pods Not Scaling

```bash
# Check HPA status
kubectl describe hpa api-hpa -n ai-platform-dev

# Check metrics server
kubectl get deployment metrics-server -n kube-system

# Check resource requests
kubectl describe pod <pod-name> -n ai-platform-dev
```

### High CPU/Memory Usage

```bash
# Profile pod
kubectl top pod <pod-name> -n ai-platform-dev

# Check processes
kubectl exec -it <pod-name> -n ai-platform-dev -- top

# Increase resource limits
kubectl set resources deployment api \
  -n ai-platform-dev \
  --limits=cpu=1,memory=2Gi \
  --requests=cpu=500m,memory=1Gi
```

### Database Connection Issues

```bash
# Check pod logs
kubectl logs statefulset/postgres -n ai-platform-dev

# Check persistent volume
kubectl get pvc -n ai-platform-dev

# Connect to database
kubectl exec -it postgres-0 -n ai-platform-dev -- psql -U postgres
```

### Network Issues

```bash
# Test connectivity
kubectl run -it --image=busybox:1.35 debug -n ai-platform-dev -- sh

# Ping services
nslookup api-service.ai-platform-dev.svc.cluster.local
nslookup postgres.ai-platform-dev.svc.cluster.local
```

## Upgrades & Maintenance

### Rolling Deployment Updates

```bash
# Update image
kubectl set image deployment/api \
  api=gcr.io/project/api:v2.0 \
  -n ai-platform-dev

# Check rollout status
kubectl rollout status deployment/api -n ai-platform-dev

# Rollback if needed
kubectl rollout undo deployment/api -n ai-platform-dev
```

### Cluster Upgrades

```bash
# GKE auto-upgrades nodes
# Check upgrade status
gcloud container operations list --zone us-central1

# Manual upgrade
gcloud container clusters upgrade cluster-name \
  --master \
  --cluster-version=1.27.0
```

## Cost Estimation

### Monthly Costs (Approximate)

**Development**
```
GKE Cluster:        $0 (free tier)
Compute:           $30-50 (preemptible)
Storage:           $5-10 (20Gi)
Networking:        $0 (internal only)
Total:             ~$35-60/month
```

**Staging**
```
GKE Cluster:       $10
Compute:           $100-150 (standard)
Storage:           $10-15 (50Gi SSD)
Networking:        $10 (ingress)
Total:             ~$130-185/month
```

**Production**
```
GKE Cluster:       $20
Compute:           $300-500 (standard HA)
Storage:           $50-100 (200Gi SSD)
Networking:        $30 (ingress + egress)
Load Balancer:     $20 (ingress)
Total:             ~$420-670/month
```

## Best Practices

1. **Always use resource requests/limits**
2. **Enable autoscaling on deployments**
3. **Use namespaces per environment**
4. **Implement network policies**
5. **Monitor actively**
6. **Test failure scenarios**
7. **Automate deployments**
8. **Keep images small**
9. **Use health checks**
10. **Document runbooks**

## Next Steps

1. Deploy to GKE via Terraform + kubectl
2. Configure external DNS
3. Set up certificate management (cert-manager)
4. Implement Ingress Controller (Nginx)
5. Enable autoscaling
6. Configure monitoring/alerting
7. Set up log aggregation
8. Implement backup/restore procedures
9. Create runbooks for common issues
10. Load test and optimize

## References

- [Kubernetes Documentation](https://kubernetes.io/docs)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
