# Kubernetes Infrastructure - AI Platform

Complete Kubernetes deployment configuration for AI Platform with automatic horizontal scaling, vertical pod autoscaling recommendations, cost optimization, and production-grade setup.

## 🎯 Key Features

✅ **Automatic Scaling** - HPA on API/Web services scales based on CPU/memory  
✅ **Cost Optimized** - Pay only for resources you use  
✅ **Multi-Environment** - Dev, Staging, Production configurations  
✅ **High Availability** - Pod disruption budgets, anti-affinity, readiness probes  
✅ **Monitoring** - Prometheus, Alertmanager, metrics collection  
✅ **Security** - Network policies, RBAC, non-root containers  
✅ **Helm Charts** - Easy templating and deployment  
✅ **GKE Native** - Optimized for Google Kubernetes Engine  

## 📁 File Structure

```
k8s/
├── 00-namespaces.yaml          # Namespaces, resource quotas, network policies
├── 01-api-deployment.yaml      # API service with HPA (2-10 replicas)
├── 02-web-deployment.yaml      # Frontend with HPA (2-8 replicas)
├── 03-database-statefulset.yaml # PostgreSQL with persistent storage
├── 04-redis-deployment.yaml    # Redis cache
├── 05-configmap-secrets.yaml   # Configuration & secrets per environment
├── 06-ingress.yaml             # Ingress rules & network policies
├── 07-monitoring.yaml          # Prometheus, alerts, dashboards
├── deploy.sh                   # Automated deployment script
├── helm/
│   ├── Chart.yaml              # Helm chart metadata
│   ├── values-dev.yaml         # Development values
│   ├── values-staging.yaml     # Staging values
│   └── values-production.yaml  # Production values
├── KUBERNETES_GUIDE.md         # Detailed Kubernetes guide
├── COST_OPTIMIZATION.md        # Cost analysis & optimization
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install required tools
brew install kubectl helm google-cloud-sdk

# Or with apt (Linux)
sudo apt-get install kubectl helm google-cloud-sdk

# Verify installation
kubectl version --client
helm version
gcloud --version
```

### Deploy with Script (Recommended)

```bash
# Development
./k8s/deploy.sh dev ai-platform-dev us-central1

# Staging
./k8s/deploy.sh staging ai-platform-staging us-central1

# Production
./k8s/deploy.sh production ai-platform-prod us-central1
```

### Manual Deployment

```bash
# 1. Setup GCP
gcloud auth login
gcloud config set project ai-platform-dev

# 2. Create GKE cluster (via Terraform)
cd infrastructure/terraform/gcp
terraform apply -var-file=terraform.tfvars.dev

# 3. Get credentials
gcloud container clusters get-credentials ai-platform-dev-gke-cluster --region us-central1

# 4. Deploy manifests
kubectl apply -f k8s/00-namespaces.yaml
kubectl apply -f k8s/01-api-deployment.yaml
kubectl apply -f k8s/02-web-deployment.yaml
kubectl apply -f k8s/03-database-statefulset.yaml
kubectl apply -f k8s/04-redis-deployment.yaml
kubectl apply -f k8s/05-configmap-secrets.yaml
kubectl apply -f k8s/06-ingress.yaml
kubectl apply -f k8s/07-monitoring.yaml
```

### Deploy with Helm

```bash
# Development
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-dev.yaml \
  -n ai-platform-dev \
  --create-namespace

# Staging
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-staging.yaml \
  -n ai-platform-staging \
  --create-namespace

# Production
helm install ai-platform ./k8s/helm \
  -f ./k8s/helm/values-production.yaml \
  -n ai-platform-production \
  --create-namespace
```

## 📊 Auto-Scaling Configuration

### Horizontal Pod Autoscaling (HPA)

Each environment has different scaling limits to optimize costs:

**Development**
```yaml
API:      min 2, max 10 replicas
Web:      min 2, max 8 replicas
Metrics:  CPU 50%, Memory 70%
```

**Staging**
```yaml
API:      min 3, max 15 replicas
Web:      min 3, max 10 replicas
Metrics:  CPU 50%, Memory 70%
```

**Production**
```yaml
API:      min 5, max 50 replicas
Web:      min 5, max 30 replicas
Metrics:  CPU 50%, Memory 70%
Pod Disruption Budget: min available 2
```

### Monitor Scaling

```bash
# Watch HPA in real-time
kubectl get hpa -n ai-platform-dev --watch

# View current replicas
kubectl get deployment -n ai-platform-dev

# Check metrics
kubectl top pods -n ai-platform-dev
kubectl top nodes

# View HPA events
kubectl describe hpa api-hpa -n ai-platform-dev
```

## 💰 Cost Optimization

### Monthly Cost Breakdown

| Environment | Compute | Storage | Network | Total |
|-------------|---------|---------|---------|-------|
| Development | $20-30 | $1 | $0 | ~$25 |
| Staging | $100-150 | $8 | $10 | ~$230 |
| Production | $300-500 | $34 | $50 | ~$595 |

### Cost Reduction Strategies

1. **Preemptible Nodes** (Dev): 70-90% cheaper
2. **Auto-Scaling**: Pay only for what you use
3. **Right-Sizing**: Optimized resource requests
4. **Scheduled Scaling**: Scale down at night
5. **Reserved Instances**: 25-52% discount (if committed)

See [COST_OPTIMIZATION.md](COST_OPTIMIZATION.md) for detailed analysis.

## 📈 Monitoring & Alerts

### Prometheus Metrics

Auto-collected metrics include:
- HTTP request count/latency
- Container CPU/memory usage
- Pod restart counts
- Database connections
- Redis memory usage

### Alert Rules

Critical alerts:
- Error rate > 5% for 5 minutes
- API latency > 2 seconds (P95)
- Memory usage > 85% of limit
- Pods restarting repeatedly
- Database connection pool exhausted

View alerts:
```bash
kubectl port-forward svc/prometheus-service 9090:9090 -n ai-platform-dev
# Visit http://localhost:9090
```

## 🔒 Security

### Network Policies
- Deny-all by default
- Allow only necessary traffic
- Egress to DNS for external APIs

### Pod Security
- Non-root user (1000)
- Read-only root filesystem
- No privilege escalation
- Dropped all Linux capabilities

### Secrets Management
- Kubernetes Secrets for dev
- External Secrets Operator for production
- All sensitive data encrypted

### RBAC
- Service accounts per component
- Minimal permissions
- No cluster-admin roles

## 🛠️ Common Operations

### View Logs

```bash
# API logs
kubectl logs -f deployment/api -n ai-platform-dev

# Web logs
kubectl logs -f deployment/web -n ai-platform-dev

# Database logs
kubectl logs -f statefulset/postgres -n ai-platform-dev

# Filter logs
kubectl logs deployment/api -n ai-platform-dev | grep ERROR
```

### Execute Commands

```bash
# Connect to API pod
kubectl exec -it <pod-name> -n ai-platform-dev -- /bin/bash

# Connect to database
kubectl exec -it postgres-0 -n ai-platform-dev -- psql -U postgres -d ai_platform

# Check Redis
kubectl exec -it <redis-pod> -n ai-platform-dev -- redis-cli
```

### Port Forwarding

```bash
# API
kubectl port-forward svc/api-service 8000:8000 -n ai-platform-dev

# Web
kubectl port-forward svc/web-service 3000:3000 -n ai-platform-dev

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ai-platform-dev

# Database
kubectl port-forward svc/postgres 5432:5432 -n ai-platform-dev
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/api \
  api=gcr.io/project/api:v2.0 \
  -n ai-platform-dev

# Check status
kubectl rollout status deployment/api -n ai-platform-dev

# Rollback if needed
kubectl rollout undo deployment/api -n ai-platform-dev
```

### Scaling

```bash
# Manual scale
kubectl scale deployment api --replicas=5 -n ai-platform-dev

# Check current replicas
kubectl get deployment -n ai-platform-dev

# View HPA decisions
kubectl get hpa -n ai-platform-dev -o wide
```

## 🐛 Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n ai-platform-dev

# View logs
kubectl logs <pod-name> -n ai-platform-dev

# Check events
kubectl get events -n ai-platform-dev --sort-by='.lastTimestamp'
```

### Pods not scaling

```bash
# Check HPA status
kubectl get hpa api-hpa -n ai-platform-dev
kubectl describe hpa api-hpa -n ai-platform-dev

# Verify metrics available
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes

# Check resource requests
kubectl describe pod <pod-name> -n ai-platform-dev
```

### High resource usage

```bash
# View pod metrics
kubectl top pods -n ai-platform-dev

# Profile specific pod
kubectl exec <pod-name> -n ai-platform-dev -- ps aux
kubectl exec <pod-name> -n ai-platform-dev -- top

# Check node resources
kubectl top nodes
kubectl describe nodes
```

### Networking issues

```bash
# Test DNS
kubectl run debug --image=busybox:1.35 -it --rm -n ai-platform-dev -- nslookup api-service

# Check service endpoints
kubectl get endpoints -n ai-platform-dev

# View network policies
kubectl get networkpolicies -n ai-platform-dev
```

## 📚 Documentation

- [KUBERNETES_GUIDE.md](KUBERNETES_GUIDE.md) - Comprehensive Kubernetes guide
- [COST_OPTIMIZATION.md](COST_OPTIMIZATION.md) - Detailed cost analysis
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Kubernetes Official Docs](https://kubernetes.io/docs)

## 🔄 Environment Variables

All environment-specific configuration is in [05-configmap-secrets.yaml](05-configmap-secrets.yaml):

**Development**
```
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=info
WORKERS=4
```

**Staging**
```
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=info
WORKERS=8
```

**Production**
```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning
WORKERS=16
ENABLE_METRICS=true
ENABLE_TRACING=true
```

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] gcloud authenticated
- [ ] kubectl installed and configured
- [ ] GKE cluster created
- [ ] Namespaces created
- [ ] Secrets and ConfigMaps deployed
- [ ] PostgreSQL running
- [ ] Redis running
- [ ] API deployed and healthy
- [ ] Web deployed and healthy
- [ ] Ingress configured
- [ ] Monitoring active
- [ ] HPA scaling verified
- [ ] Logs accessible
- [ ] Backups configured

## 🚨 Important Notes

1. **Production Secrets**: Do NOT store sensitive data in YAML files
   - Use External Secrets Operator
   - Use Sealed Secrets
   - Use Google Secret Manager

2. **Database Backups**: Configure automated backups
   - Daily at 2 AM UTC
   - 30-day retention
   - Test restore procedures

3. **Cost Monitoring**: Review costs weekly
   - Set budget alerts
   - Analyze usage patterns
   - Optimize underutilized resources

4. **Scaling Tests**: Load test before production
   - Verify HPA works
   - Check database performance
   - Monitor memory/CPU during scaling

## 🎓 Learning Resources

- [Kubernetes Concepts](https://kubernetes.io/docs/concepts/)
- [HPA Guide](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

## 📞 Support

For issues or questions:
1. Check logs: `kubectl logs <pod-name> -n <namespace>`
2. Describe resources: `kubectl describe <resource> <name> -n <namespace>`
3. Check events: `kubectl get events -n <namespace>`
4. Review KUBERNETES_GUIDE.md troubleshooting section

## 📝 License

AI Platform - All Rights Reserved
