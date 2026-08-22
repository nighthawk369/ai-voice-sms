# Kubernetes Cost Optimization - AI Platform

## Strategy Overview

Optimize cloud usage with automatic scaling, efficient resource allocation, and environment-appropriate sizing. Scale only when needed, pay only for what you use.

## Cost Model

### GKE Cluster Costs

| Component | Dev | Staging | Production |
|-----------|-----|---------|------------|
| Control Plane | Free | $0.10/hr (~$73/mo) | $0.10/hr (~$73/mo) |
| Network Ingress | Free | Free | Free |
| Network Egress | ~$0.12/GB | ~$0.12/GB | ~$0.12/GB |

### Compute Costs (Hourly Rates)

**GCE Machine Types**

```
e2-standard-2    (dev/preemptible)     = $0.0336/hr × 24 × 30 = $24.19/mo
n1-standard-2    (staging)              = $0.0955/hr × 24 × 30 = $68.76/mo
n1-standard-4    (production)           = $0.1910/hr × 24 × 30 = $137.52/mo
```

**Preemptible Discounts**
```
Preemptible nodes = 70-90% cheaper
e2-standard-2 preemptible = $0.0101/hr × 24 × 30 = $7.27/mo
```

### Storage Costs

```
pd-standard  = $0.04/GB/month
pd-ssd       = $0.17/GB/month
pd-balanced  = $0.10/GB/month

Development (20 GB standard)   = 20 × $0.04 = $0.80/mo
Staging (50 GB SSD)            = 50 × $0.17 = $8.50/mo
Production (200 GB SSD)        = 200 × $0.17 = $34/mo
```

## Environment-Specific Optimization

### Development Environment

**Goal**: Minimize cost for testing
**Strategy**: Use preemptible nodes, minimal replicas

```yaml
Node Pool:
  - Machine type: e2-standard-2 (preemptible)
  - Min nodes: 1
  - Max nodes: 3
  - Cost: ~$7.27/node/mo

Pod Configuration:
  - API min replicas: 2
  - Web min replicas: 2
  - Database: single replica
  - Storage: 20 GB standard

Monthly Cost Breakdown:
  Cluster:       $0 (free)
  Compute:       $22/mo (3 nodes × $7.27)
  Storage:       $1/mo
  Networking:    $0
  ────────────────
  Total:         ~$23/mo
```

**Optimization Techniques**:
1. ✅ Use preemptible nodes (70-90% discount)
2. ✅ Single node cluster for local development
3. ✅ Shared storage across services
4. ✅ No redundancy needed
5. ✅ Aggressive pod auto-scaling down
6. ✅ Minimal resource requests

### Staging Environment

**Goal**: Balance cost and production-like behavior
**Strategy**: Standard nodes, moderate replicas, some redundancy

```yaml
Node Pool:
  - Machine type: n1-standard-2
  - Min nodes: 2
  - Max nodes: 5
  - Cost: ~$68.76/node/mo

Pod Configuration:
  - API min replicas: 3
  - Web min replicas: 3
  - Database: single replica (optional HA)
  - Storage: 50 GB SSD

Monthly Cost Breakdown:
  Cluster:       $73/mo (master)
  Compute:       $138/mo (2 nodes min × $68.76)
  Storage:       $8.50/mo
  Networking:    $10/mo (ingress)
  ────────────────
  Total:         ~$230/mo
```

**Optimization Techniques**:
1. ✅ Standard nodes with auto-repair
2. ✅ Moderate replica count
3. ✅ Auto-scaling: min 2, max 5
4. ✅ SSD storage for faster access
5. ✅ Realistic load testing
6. ✅ Cost alerts enabled

### Production Environment

**Goal**: Performance and reliability, pay for quality
**Strategy**: Regional nodes, high availability, comprehensive monitoring

```yaml
Node Pool:
  - Machine type: n1-standard-4
  - Min nodes: 3 (regional HA)
  - Max nodes: 20
  - Cost: ~$137.52/node/mo

Pod Configuration:
  - API min replicas: 5
  - Web min replicas: 5
  - Database: 1 primary + backups
  - Storage: 200 GB SSD

Monthly Cost Breakdown:
  Cluster:       $73/mo (master)
  Compute:       $413/mo (3 nodes min × $137.52)
  Storage:       $34/mo
  Networking:    $50/mo (ingress + egress)
  Load Balancer: $20/mo
  Backups:       $5/mo
  ────────────────
  Total:         ~$595/mo
```

**Optimization Techniques**:
1. ✅ Regional HA across zones
2. ✅ Pod disruption budgets
3. ✅ Efficient auto-scaling (min 5, max 50)
4. ✅ SSD for performance
5. ✅ Comprehensive monitoring
6. ✅ Reserved instances (if >6 months)

## Cost Reduction Strategies

### 1. Right-Sizing Resources

**Current (Optimized)**
```yaml
API:
  requests: cpu: 200m, memory: 256Mi
  limits:   cpu: 500m, memory: 512Mi
  → 2 pods = 400m CPU, 512Mi memory

Web:
  requests: cpu: 100m, memory: 128Mi
  limits:   cpu: 250m, memory: 256Mi
  → 2 pods = 200m CPU, 256Mi memory

Total per node: 600m CPU (2.4 GHz), 768Mi memory
Node capacity:  2000m CPU (8 GHz), 3.75 GB memory
Utilization:    30% CPU, 20% memory → Good packing
```

**Cost Impact**: $0 (optimal sizing)

### 2. Pod Auto-Scaling

**Aggressive Scale-Down**
```yaml
API HPA:
  scaleDown:
    stabilization: 300s (5 minutes)
    policy: 50% reduction per minute

Example: 5 pods → 3 pods (50%) → 2 pods (50%) → min 2
→ Saves: 3 pods × 256Mi = 768Mi memory, 300m CPU
→ Cost reduction: ~$0.50/day per pod
```

**Smart Scale-Up**
```yaml
scaleUp:
  stabilization: 0s (immediate)
  policy: 100% increase per 30s

Example: 2 pods → 4 pods → 8 pods → max 10
→ Ensures performance when needed
→ No unnecessary cost during scale-up
```

**Cost Impact**: 20-30% savings during low-traffic periods

### 3. Reserved Instances (Long-term)

For production workloads >6 months:

```
Standard Instance:   $137.52/node/mo
Reserved 1-year:     $1200/node (= $100/mo)
Reserved 3-year:     $3000/node (= $83/mo)

Savings with 3 nodes:
- Monthly: 3 × $137.52 = $412.56
- Reserved 1yr: 3 × $100 = $300/mo (-27%)
- Reserved 3yr: 3 × $83 = $249/mo (-40%)
```

**Cost Impact**: 25-40% reduction for stable workloads

### 4. Committed Use Discounts

GCP Committed Use Discounts (CUDs):

```
1-year commitment:   25% discount
3-year commitment:   52% discount

e2-standard-2 CUD:
  3-year = $24.19 × 0.48 = $11.61/mo

n1-standard-4 CUD:
  3-year = $137.52 × 0.48 = $66/mo
```

**Cost Impact**: 25-52% reduction for committed resources

### 5. Workload Consolidation

**Before**: Separate namespaces
```
Dev:        1 node × $7.27 = $7.27
Staging:    2 nodes × $68.76 = $137.52
Production: 3 nodes × $137.52 = $412.56
────────────────────────────────
Total:      $557.35/mo
```

**After**: Shared cluster, different namespaces
```
Shared cluster: 3 nodes × $68.76 = $206.28
- Dev pods: 1 preemptible slot
- Staging: 2 standard slots
- Production: 3 standard slots
────────────────────────────────
Total:      $206.28/mo (-63%)
```

**Cost Impact**: 50-70% reduction with careful scheduling

### 6. Scheduled Scaling

Scale down during off-hours:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: api-schedule
spec:
  scaleTargetRef:
    name: api
  triggers:
  - type: cron
    metadata:
      timezone: UTC
      start: 0 22 * * *           # 10 PM - scale down
      end: 0 7 * * 1-5            # 7 AM weekdays - scale up
      desiredReplicas: '1'        # 1 replica at night
  minReplicaCount: 1
  maxReplicaCount: 10

Savings:
- 5 replicas × 512Mi = 2.56 GB for 9 hours daily
- 5 replicas × (500m + 250m) = 3.75 cores for 9 hours
- ~$150/month for off-peak
```

**Cost Impact**: 20-30% reduction with 24/7 services

### 7. Monitoring and Alerts

```yaml
# Alert when CPU usage < 20% (over-provisioned)
- alert: UnderutilizedCPU
  expr: avg(rate(container_cpu_usage_seconds_total[5m])) < 0.2
  for: 1h

# Alert when memory usage > 85% (scale needed)
- alert: HighMemoryUsage
  expr: avg(container_memory_usage_bytes) / container_spec_memory_limit_bytes > 0.85
  for: 5m

# Alert on cost anomaly
- alert: UnexpectedCostIncrease
  expr: increase(gke_billing_monthly_cost_usd[1d]) > 1.5
```

**Cost Impact**: Proactive optimization saves 10-20%

## Cost Comparison: Terraform vs Kubernetes

### Terraform (Cloud Run/Cloud SQL)

```
Cloud Run:
  per CPU:   $0.00002400/second = $1.73/month per 1 CPU
  per GB:    $0.00000250/second = $0.18/month per 1 GB
  Example:   5 services × 2 CPU × $1.73 = $17.30/mo

Cloud SQL:
  db-f1-micro:  $10/month
  db-n1-standard-1: $50/month

Total (Dev):     ~$30-50/month
Total (Staging): ~$150-200/month
Total (Prod):    ~$400-600/month
```

### Kubernetes (GKE)

```
GKE Cluster + Nodes:
  Development:  ~$23/month
  Staging:      ~$230/month
  Production:   ~$595/month

Savings vs Cloud Run:
  Dev:     -25% (Kubernetes cheaper)
  Staging: +0% (Comparable)
  Prod:    +30% (Cloud Run cheaper at scale)
```

**Recommendation**: Use Kubernetes when:
- Workloads exceed 5-10 concurrent instances
- You need fine-grained resource control
- Multi-service orchestration needed
- Long-term deployment (>6 months)

## Cost Monitoring

### GCP Cost Dashboard

```bash
# Export billing data
bq query --use_legacy_sql=false '
  SELECT
    billing_account_id,
    service.description,
    sku.description,
    usage.amount_in_pricing_units as usage,
    cost_type,
    amount_micros/1000000 as amount_usd
  FROM `<PROJECT_ID>.billing_dataset.gcp_billing_export_v1_*`
  WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY 1,2,3,4,5,6
  ORDER BY amount_usd DESC
'

# View GKE-specific costs
gke_cost=$(bq query --use_legacy_sql=false --format=csv '
  SELECT SUM(amount_micros)/1000000
  FROM `<PROJECT_ID>.billing_dataset.gcp_billing_export_v1_*`
  WHERE service.id = "6F81-5844-456A"  -- GKE
  AND DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
' | tail -1)
echo "GKE costs: \$$gke_cost"
```

### Kubernetes Resource Metrics

```bash
# Total resource requests
kubectl describe nodes -n ai-platform-dev | grep -A 5 "Allocated resources"

# Pod cost estimation
kubectl get pods -n ai-platform-dev -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources.requests.cpu}{"\t"}{.spec.containers[*].resources.requests.memory}{"\n"}{end}'

# Monthly cost per pod
pod_cpu=500m  # 0.5 CPU
pod_memory=512Mi  # 0.5 GB
pod_cost=$(echo "scale=2; 0.5 * 1.73 + 0.5 * 0.18" | bc)
echo "Pod monthly cost: \$$pod_cost"
```

## Cost Targets

### Monthly Budget

```
Development:   $25  (preemptible nodes)
Staging:       $250 (standard nodes)
Production:    $600 (HA setup)
Total:         $875/month for all 3 environments
```

### per Request Cost

```
API Request:   $0.00001/request (estimate)
  - Compute:   $0.000005
  - Storage:   $0.000003
  - Network:   $0.000002

Example:
  1M requests/day × $0.00001 = $10/day = $300/month
  10M requests/day × $0.00001 = $100/day = $3,000/month
```

## Optimization Roadmap

### Phase 1: Baseline (Week 1)
- [ ] Deploy to GKE
- [ ] Enable monitoring
- [ ] Set resource requests/limits
- [ ] Document current costs

### Phase 2: Optimization (Week 2-3)
- [ ] Enable HPA on all deployments
- [ ] Configure pod auto-scaling
- [ ] Optimize resource requests
- [ ] Set cost alerts

### Phase 3: Advanced (Week 4+)
- [ ] Implement scheduled scaling
- [ ] Add vertical pod autoscaler
- [ ] Evaluate reserved instances
- [ ] Consolidate workloads

### Phase 4: Continuous (Ongoing)
- [ ] Monitor metrics weekly
- [ ] Adjust resources quarterly
- [ ] Review CUD options annually
- [ ] Optimize application code

## Checklist

- [ ] Resource requests/limits defined per pod
- [ ] HPA enabled on all deployments
- [ ] Pod min/max replicas appropriate
- [ ] Monitoring dashboards created
- [ ] Cost alerts configured
- [ ] Backup/restore procedures documented
- [ ] Scaling tested under load
- [ ] Failure scenarios tested
- [ ] Regular cost reviews scheduled
- [ ] Team trained on cost monitoring

## Expected Savings

| Strategy | Savings | Effort |
|----------|---------|--------|
| Right-sizing | 10-20% | Low |
| Auto-scaling | 20-40% | Medium |
| Preemptible | 70-90% | Medium |
| Reserved instances | 25-52% | High |
| Scheduled scaling | 20-30% | Medium |
| **Total potential** | **~60-70%** | High |

## Conclusion

Kubernetes on GKE provides excellent cost optimization opportunities through:
1. **Efficient auto-scaling** (pay only for what you use)
2. **Right-sizing** (avoid over-provisioning)
3. **Preemptible nodes** (dev environment savings)
4. **Reserved instances** (long-term commitments)
5. **Consolidated clusters** (shared resources)

**Target**: Achieve $25 dev + $250 staging + $600 production = **$875/month** for complete infrastructure.
