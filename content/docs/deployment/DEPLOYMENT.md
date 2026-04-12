# Synapto Platform — Deployment & Operations Manual

> **Version:** 1.0 | **Classification:** Internal — Engineering & DevOps  
> **Last Updated:** April 2026 | **Maintained by:** Platform Engineering

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Build Phase — Image Creation & Registry](#build-phase--image-creation--registry)
5. [Deployment: Standalone Docker](#deployment-standalone-docker)
6. [Deployment: Kubernetes (Multi-Cloud)](#deployment-kubernetes-multi-cloud)
   - [Cloud-Specific Provisioning](#cloud-specific-provisioning)
   - [AKS — Azure Kubernetes Service](#aks--azure-kubernetes-service)
   - [EKS — Amazon Elastic Kubernetes Service](#eks--amazon-elastic-kubernetes-service)
   - [GKE — Google Kubernetes Engine](#gke--google-kubernetes-engine)
   - [UpCloud Managed Kubernetes](#upcloud-managed-kubernetes)
   - [Applying Manifests](#applying-manifests)
7. [Configuration Reference](#configuration-reference)
8. [Validation & Health Checks](#validation--health-checks)
9. [Operations Runbook](#operations-runbook)
10. [Security Hardening](#security-hardening)
11. [Rollback Procedures](#rollback-procedures)

---

## Introduction

This manual provides authoritative, step-by-step instructions for building, deploying, and operating the Synapto Autonomous Remediation Platform. It covers two deployment targets:

- **Standalone Docker** — A single-host environment using Docker Compose, suitable for development, staging, or small production deployments.
- **Kubernetes (Multi-Cloud)** — A production-grade, horizontally scalable environment targeting Azure AKS, AWS EKS, Google GKE, and UpCloud Managed Kubernetes, using a shared **Kustomize base** with per-cloud **overlays**.

All manifests live under `infrastructure/kubernetes/`.

---

## Architecture Overview

Synapto is a fully containerised microservices platform. The following services are deployed:

| Service | Internal Port | Role |
|:---|:---:|:---|
| `postgres` | 5432 | Primary relational store (incidents, users, SOPs) |
| `redis` | 6379 | Real-time cache, pub/sub event bus |
| `integration-layer` | 8001 | Normalises events from Prometheus, CloudWatch, webhooks |
| `orchestration-layer` | 8002 | Classifies incidents, drives remediation workflow |
| `knowledge-layer` | 8003 | SOP library, policies, playbooks, topology graph |
| `execution-engine` | 8004 | Executes scripts via SSH, WinRM, Netmiko, SQL |
| `learning-engine` | 8005 | AI-driven diagnostics; SOP auto-promotion |
| `auth-service` | 8006 | JWT issuance and user authentication |
| `admin-service` | 8007 | Tenant and user management |
| `itsm-connector` | 8008 | ServiceNow, Jira, PagerDuty integration |
| `agent-service` | 50051 | mTLS-secured gRPC server for remote agents |
| `api-gateway` | 8000 | Unified public API entry point |
| `frontend` | 80 | React/Vite SPA served via nginx |

---

## Prerequisites

### Required Tools

Ensure the following tools are installed and on your `$PATH` before proceeding.

#### For all deployment targets

| Tool | Minimum Version | Install |
|:---|:---:|:---|
| Docker Engine | 25.0+ | https://docs.docker.com/engine/install/ |
| Docker Compose v2 | 2.24+ | Bundled with Docker Desktop |
| `git` | 2.40+ | https://git-scm.com/ |

#### For Kubernetes deployments (additionally)

| Tool | Minimum Version | Install |
|:---|:---:|:---|
| `kubectl` | 1.30+ | https://kubernetes.io/docs/tasks/tools/ |
| `kustomize` | 5.3+ | https://kubectl.docs.kubernetes.io/installation/kustomize/ |
| `helm` | 3.14+ | https://helm.sh/docs/intro/install/ (for cert-manager) |

#### Cloud-specific CLIs

| Cloud | CLI Tool | Install |
|:---|:---:|:---|
| Azure AKS | `az` (Azure CLI) v2.57+ | https://learn.microsoft.com/cli/azure/install-azure-cli |
| AWS EKS | `aws` CLI v2 + `eksctl` | https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html |
| Google GKE | `gcloud` CLI | https://cloud.google.com/sdk/docs/install |
| UpCloud | `upctl` | https://developers.upcloud.com/1.3/tools |

### Required Permissions

| Target | Minimum IAM Role / Permission |
|:---|:---|
| Docker host | `sudo` or membership in the `docker` group |
| Azure AKS | `Contributor` on the resource group; `AcrPush` on the container registry |
| AWS EKS | `eks:*`, `ec2:*`, `iam:CreateRole`, `ecr:*` |
| Google GKE | `roles/container.admin`, `roles/storage.admin` |
| UpCloud | Object Storage admin + Kubernetes cluster admin |

> [!IMPORTANT]
> All sensitive values (passwords, API keys, secrets) **must** be sourced from a secrets manager (Azure Key Vault, AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault) in production. **Never commit raw secret values to source control.**

---

## Build Phase — Image Creation & Registry

### How Docker Compose Builds Images

Docker Compose's `build:` directive instructs Compose to build a local image from a `Dockerfile` before running the container, as opposed to pulling a pre-built image. This is defined in `docker-compose.yml`:

```yaml
# Example: api-gateway service build configuration
api-gateway:
  build:
    context: ./backend        # Build context — files available to the Dockerfile
    dockerfile: api-gateway/Dockerfile  # Path to the Dockerfile, relative to context
```

When you run `docker compose build`, Compose:
1. Sends the `context` directory to the Docker daemon.
2. Executes the `Dockerfile` instructions to produce a local image.
3. Tags the result with the service name (e.g., `synapto-gateway`).

### Building All Images

```bash
# Build all service images in parallel (recommended)
docker compose build --parallel

# Build a single service
docker compose build api-gateway
```

### Tagging & Pushing to a Private Registry

Synapto ships with `deploy-docker.sh` to automate the build → tag → push pipeline.

```bash
# Make the script executable (first time only)
chmod +x deploy-docker.sh

# Full pipeline: build, tag with git SHA, and push
./deploy-docker.sh \
  --registry registry.example.com/synapto \
  --tag 1.4.2 \
  --push
```

#### Manual equivalent for a single image

```bash
# 1. Authenticate to your registry
docker login registry.example.com

# 2. Build (already built above, but shown for completeness)
docker compose build api-gateway

# 3. Tag with registry prefix and semantic version
docker tag synapto-gateway registry.example.com/synapto/api-gateway:1.4.2
docker tag synapto-gateway registry.example.com/synapto/api-gateway:latest

# 4. Push both tags
docker push registry.example.com/synapto/api-gateway:1.4.2
docker push registry.example.com/synapto/api-gateway:latest
```

### Image Versioning Strategy

| Tag | Purpose | Example |
|:---|:---|:---|
| `latest` | Always points to the most recently pushed build | `api-gateway:latest` |
| Semantic version | Human-readable release pinning | `api-gateway:1.4.2` |
| Git short SHA | Exact, reproducible artifact reference | `api-gateway:a3f8c91` |

> [!TIP]
> In production pipelines, use the Git SHA tag in Kubernetes manifests. This guarantees that a deployment always references an exact, immutable artefact and prevents accidental rollouts caused by an `latest` tag re-pull.

### Registry Authentication Reference

| Registry | Command |
|:---|:---|
| Docker Hub | `docker login` |
| Azure Container Registry | `az acr login --name <registry-name>` |
| AWS ECR | `aws ecr get-login-password --region <region> \| docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com` |
| Google Artifact Registry | `gcloud auth configure-docker <region>-docker.pkg.dev` |
| Generic / Self-hosted | `docker login <registry-host>` |

---

## Deployment: Standalone Docker

### First-Time Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/synapto.git
cd synapto

# 2. Configure environment
cp .env.example .env
# Edit .env and set all REPLACE_ME values, particularly:
#   SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD
nano .env

# 3. Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

The script executes the following phases automatically:
1. **Preflight** — validates Docker, Compose, and all required `.env` keys.
2. **Build** — builds all service images in parallel.
3. **Infrastructure** — starts Postgres and Redis; waits for health checks.
4. **Migrations** — applies SQL migrations and seeds SOP data.
5. **Application** — starts all backend and frontend services.
6. **Admin Seed** — creates the default admin user with an Argon2id password hash.
7. **Validation** — checks the health status of every container.

### Subsequent Deployments (Update)

```bash
# Rebuild images and restart all services (data preserved)
./deploy.sh --update
```

### Management Commands

```bash
# View real-time logs for all services
docker compose logs -f

# View logs for a specific service
docker compose logs -f api-gateway

# Stop all services (data preserved)
./deploy.sh --stop

# DESTROY environment (removes all containers AND volumes — DATA LOSS)
./deploy.sh --destroy
```

---

## Deployment: Kubernetes (Multi-Cloud)

All Kubernetes configuration is organised using **Kustomize**:

```
infrastructure/kubernetes/
├── base/                    ← Shared, cloud-agnostic manifests
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml         ← Template only; populate at deploy time
│   ├── storage.yaml         ← PVCs (storage class patched by overlays)
│   ├── deployment.yaml      ← All service Deployments
│   ├── service.yaml         ← ClusterIP + LoadBalancer services
│   └── ingress.yaml         ← Ingress with TLS + WebSocket support
└── overlays/
    ├── aks/                 ← Azure patches
    ├── eks/                 ← AWS patches
    ├── gke/                 ← GCP patches
    └── upcloud/             ← UpCloud patches
```

### Pre-Deployment: Prepare Secrets

> [!CAUTION]
> Never apply `secrets.yaml` directly from source control. It contains placeholder values and **will expose your environment** if applied as-is.

The recommended approach is to generate the secret from your live `.env` file:

```bash
# Generate and apply the secret from your .env file
kubectl create secret generic synapto-secrets \
  --namespace synapto \
  --from-env-file=.env \
  --dry-run=client -o yaml | kubectl apply -f -
```

For mTLS (required by the agent-service):

```bash
# Upload the generated certificates as a secret
kubectl create secret generic synapto-mtls-certs \
  --namespace synapto \
  --from-file=ca.crt=./certs/ca.crt \
  --from-file=server.crt=./certs/server.crt \
  --from-file=server.key=./certs/server.key \
  --from-file=ed25519_signing.key=./certs/ed25519_signing.key
```

### Pre-Deployment: Process Image References

Before applying manifests, substitute the `REGISTRY` and `TAG` placeholders in `deployment.yaml`:

```bash
# Example: replace placeholders for a release
REGISTRY="registry.example.com/synapto"
TAG="1.4.2"

sed -i "s|REGISTRY|${REGISTRY}|g" infrastructure/kubernetes/base/deployment.yaml
sed -i "s|TAG|${TAG}|g"           infrastructure/kubernetes/base/deployment.yaml
```

---

### Cloud-Specific Provisioning

#### AKS — Azure Kubernetes Service

```bash
# 1. Login and set subscription
az login
az account set --subscription "<SUBSCRIPTION_ID>"

# 2. Create resource group (if not already created)
az group create --name synapto-rg --location westeurope

# 3. Create AKS cluster (adjust node-count and vm-size for your workload)
az aks create \
  --resource-group synapto-rg \
  --name synapto-aks \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# 4. Point kubectl to the AKS cluster
az aks get-credentials \
  --resource-group synapto-rg \
  --name synapto-aks

# 5. Verify connectivity
kubectl get nodes
```

**Required add-ons for AKS:**
- Azure Application Gateway Ingress Controller (AGIC) or nginx-ingress
- cert-manager (for TLS via Let's Encrypt)

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true
```

---

#### EKS — Amazon Elastic Kubernetes Service

```bash
# 1. Configure AWS CLI
aws configure     # Enter Access Key ID, Secret, Region

# 2. Create EKS cluster using eksctl
eksctl create cluster \
  --name synapto-eks \
  --region eu-west-1 \
  --nodegroup-name synapto-nodes \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 6 \
  --managed

# 3. Point kubectl to EKS (eksctl does this automatically, but for clarity)
aws eks update-kubeconfig \
  --region eu-west-1 \
  --name synapto-eks

# 4. Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=synapto-eks

# 5. Verify
kubectl get nodes
```

---

#### GKE — Google Kubernetes Engine

```bash
# 1. Authenticate and set project
gcloud auth login
gcloud config set project <PROJECT_ID>

# 2. Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# 3. Create GKE cluster (Autopilot recommended for managed nodes)
gcloud container clusters create-auto synapto-gke \
  --region europe-west1

# 4. Point kubectl to GKE
gcloud container clusters get-credentials synapto-gke \
  --region europe-west1

# 5. Verify
kubectl get nodes

# 6. Configure Docker for Artifact Registry
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

---

#### UpCloud Managed Kubernetes

```bash
# 1. Authenticate
upctl account login

# 2. Create a cluster (via UI or CLI)
#    UI: https://hub.upcloud.com → Kubernetes → Create cluster
#    Recommended: 3 worker nodes, 4vCPU/8GB plan

# 3. Download kubeconfig
upctl kubernetes config <CLUSTER_UUID> > ~/.kube/upcloud-synapto.yaml
export KUBECONFIG=~/.kube/upcloud-synapto.yaml

# 4. Verify
kubectl get nodes

# 5. Install nginx-ingress (UpCloud does not provide a native IC)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# 6. Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true
```

---

### Applying Manifests

Once `kubectl` points to your target cluster, apply the appropriate overlay:

```bash
# ── AKS ──────────────────────────────────────────────────────────────────────
kubectl apply -k infrastructure/kubernetes/overlays/aks

# ── EKS ──────────────────────────────────────────────────────────────────────
kubectl apply -k infrastructure/kubernetes/overlays/eks

# ── GKE ──────────────────────────────────────────────────────────────────────
kubectl apply -k infrastructure/kubernetes/overlays/gke

# ── UpCloud ──────────────────────────────────────────────────────────────────
kubectl apply -k infrastructure/kubernetes/overlays/upcloud
```

> [!NOTE]
> If you prefer to preview what will be applied before committing, run:
> ```bash
> kubectl apply -k infrastructure/kubernetes/overlays/aks --dry-run=client
> # or render the full manifest:
> kubectl kustomize infrastructure/kubernetes/overlays/aks
> ```

---

## Configuration Reference

All runtime configuration is injected from two Kubernetes resources:

| Resource | Type | Contents |
|:---|:---|:---|
| `synapto-config` | ConfigMap | Non-sensitive settings (hostnames, ports, feature flags) |
| `synapto-secrets` | Secret | Credentials, API keys, encryption keys |

Key variables that **must** be set before first run:

| Variable | Description | Example |
|:---|:---|:---|
| `SECRET_KEY` | Application-level signing key | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing secret | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | Field-level encryption key | `openssl rand -base64 32` |
| `POSTGRES_PASSWORD` | PostgreSQL superuser password | ≥ 20 random chars |
| `REDIS_PASSWORD` | Redis authentication password | ≥ 16 random chars |
| `ADMIN_DEFAULT_PASSWORD` | One-time bootstrapped admin password | ≥ 16 chars, mixed case + symbols |

---

## Validation & Health Checks

### Docker: Container Health

```bash
# Check the status of all containers
docker compose ps

# View resource usage
docker stats

# Check logs for a specific service
docker compose logs --tail=100 api-gateway
```

### Kubernetes: Pod Health

```bash
# List all pods in the synapto namespace
kubectl get pods -n synapto

# Describe a specific pod (shows events and probe failures)
kubectl describe pod <POD_NAME> -n synapto

# Stream logs from a deployment
kubectl logs -n synapto deployment/api-gateway -f

# Check rollout status
kubectl rollout status deployment/api-gateway -n synapto

# View resource usage (requires metrics-server)
kubectl top pods -n synapto
```

### Service Endpoint Validation

```bash
# Check all services
kubectl get svc -n synapto

# Get the external IP of the LoadBalancer (agent-service gRPC)
kubectl get svc agent-service -n synapto -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Get the Ingress address
kubectl get ingress synapto-ingress -n synapto
```

### API Health Probe

```bash
# From inside the cluster (via a debug pod)
kubectl run curl-test --image=curlimages/curl -it --restart=Never --rm -- \
  curl -s http://api-gateway.synapto.svc.cluster.local:8000/health

# From outside (replace with your domain)
curl -s https://app.synapto.io/api/v1/health | python3 -m json.tool
```

**Expected healthy response:**
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### PersistentVolume Check

```bash
# Verify all PVCs are bound
kubectl get pvc -n synapto

# Example healthy output:
# NAME           STATUS   VOLUME    CAPACITY   ACCESS MODES   STORAGECLASS
# postgres-pvc   Bound    pvc-xxx   50Gi       RWO            managed-premium
```

---

## Operations Runbook

### Scaling a Service

```bash
# Scale the api-gateway to 4 replicas
kubectl scale deployment api-gateway --replicas=4 -n synapto

# Enable Horizontal Pod Autoscaler (CPU-based)
kubectl autoscale deployment api-gateway \
  --min=2 --max=10 --cpu-percent=70 \
  -n synapto
```

### Deploying a New Image Version

```bash
# 1. Build and push the new image
./deploy-docker.sh \
  --registry registry.example.com/synapto \
  --tag 1.5.0 \
  --push

# 2. Update the image in the deployment (rolling update)
kubectl set image deployment/api-gateway \
  api-gateway=registry.example.com/synapto/api-gateway:1.5.0 \
  -n synapto

# 3. Monitor the rollout
kubectl rollout status deployment/api-gateway -n synapto
```

### Accessing a Running Pod

```bash
# Open an interactive shell in the api-gateway container
kubectl exec -it deployment/api-gateway -n synapto -- /bin/sh
```

### Running Database Migrations Manually

```bash
# Run a one-off migration Job
kubectl run db-migrate \
  --image=registry.example.com/synapto/api-gateway:1.5.0 \
  --restart=Never \
  --namespace=synapto \
  --env-from=configmap/synapto-config \
  --env-from=secret/synapto-secrets \
  -- python3 -c "
import sys; sys.path.insert(0, '/app')
from shared import init_db
init_db()
print('Migration complete.')
"
kubectl logs db-migrate -n synapto
kubectl delete pod db-migrate -n synapto
```

---

## Security Hardening

> [!WARNING]
> The default configuration is production-ready but requires the following hardening steps before accepting internet traffic.

1. **Change all default credentials** immediately after the first successful deployment.
2. **Rotate secrets** using your cloud provider's secrets manager; never store them in Git.
3. **Enable NetworkPolicies** to restrict pod-to-pod traffic to only what is required.
4. **Enable Pod Security Standards** for the `synapto` namespace:
   ```bash
   kubectl label namespace synapto pod-security.kubernetes.io/enforce=restricted
   ```
5. **Enable TLS everywhere** — the Ingress manifest is pre-configured for cert-manager; ensure your `ClusterIssuer` is operational.
6. **Audit RBAC** — Synapto does not require cluster-admin privileges; scope service account permissions to the minimum necessary.

---

## Rollback Procedures

### Kubernetes: Roll Back a Bad Deployment

```bash
# View rollout history
kubectl rollout history deployment/api-gateway -n synapto

# Roll back to the previous revision
kubectl rollout undo deployment/api-gateway -n synapto

# Roll back to a specific revision
kubectl rollout undo deployment/api-gateway --to-revision=3 -n synapto
```

### Docker: Roll Back to a Known Good Image

```bash
# Stop the failing service
docker compose stop api-gateway

# Re-tag the last good image version
docker tag registry.example.com/synapto/api-gateway:1.4.2 synapto-gateway:latest

# Restart with the known good image
docker compose up -d api-gateway
```

### Full Environment Reset (Docker)

```bash
# DANGER: This destroys all data
./deploy.sh --destroy

# Redeploy from scratch
./deploy.sh
```

---

*This document is maintained by the Synapto Platform Engineering team. For issues, open a ticket or contact `platform-eng@synapto.io`.*
