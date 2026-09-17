# Production Deployment & Operations Runbook

## 1. Hosting Architecture Justification

> [!NOTE]
> **Minimal Infrastructure Decision**:
> In accordance with simplicity and operational reliability, the system is designed to run as a unified containerized stack via **Docker Compose** on a single dedicated virtual machine (e.g. AWS EC2 `t4g.xlarge` / `c6g.xlarge` ARM64, GCP Compute Engine `t2a-standard-4`, Azure `Standard_D4ps_v5`, or equivalent on-premise Linux server).
> 
> Introducing heavy orchestration (such as Kubernetes) is explicitly avoided until horizontal scale or multi-region requirements demand it. Single-host container compose provides predictable resource isolation, minimal operational overhead, and instantaneous local rollbacks.

---

## 2. Secrets Management & Environment Isolation

All sensitive credentials and API keys are injected via environment variables at container runtime and **must never be committed to Git**.

| Secret / Config | Purpose | Recommended Secret Store |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic Claude 3 Opus API key for RAG report generation | AWS Secrets Manager / HashiCorp Vault / Host `.env.production` (chmod 600) |
| `POSTGRES_PASSWORD` | PostgreSQL database user credentials | Injected dynamically or generated via secret rotation |
| `POSTGRES_USER` | Relational DB administrative role | `pd_admin` |
| `BACKEND_CORS_ORIGINS` | Whitelist of permitted hospital/clinic portal domains | `["https://app.pdvoice.internal"]` |
| `MODEL_VERSION` | Pinned model release tag (e.g. `model_v1.0.0`) | Injected via CI/CD release workflow |

---

## 3. Image Tagging & Versioning Convention

Production container images are version-pinned according to semantic versioning and the corresponding machine learning model release:

- **Backend Image**: `pd-voice-backend:v{X.Y.Z}`
- **Frontend Image**: `pd-voice-frontend:v{X.Y.Z}`
- **Model Artifact Directory**: `model/exported/model_v{X.Y.Z}/`

---

## 4. Step-by-Step Fresh Server Deployment

### Prerequisites
- Linux host running Ubuntu 22.04 LTS / Debian 12 (ARM64 or x86_64)
- Docker Engine 24.0+ and Docker Compose v2.20+
- Port 80 and 443 accessible from the institutional network

### Step 1: Clone Repository & Restrict Permissions
```bash
git clone https://github.com/organization/pd-voice-screening.git /opt/pd-voice
cd /opt/pd-voice/deployment/production
```

### Step 2: Configure Environment Secrets
```bash
cp .env.production.example .env.production
chmod 600 .env.production
# Edit secrets in .env.production with production API keys and strong DB passwords
nano .env.production
```

### Step 3: Launch Production Stack
```bash
./deploy.sh v1.0.0
```

### Step 4: Verify System Health
```bash
curl -s http://localhost:8000/api/v1/health | jq .
```
Expected output:
```json
{
  "status": "healthy",
  "model_version": "model_v1.0.0",
  "timestamp": "2026-08-23T17:30:00.000000+00:00",
  "services": {
    "database": "connected",
    "vector_db": "connected"
  }
}
```

---

## 5. Versioned Upgrade Workflow

When deploying a new release (e.g., upgrading from `v1.0.0` to `v1.0.1`):

1. Ensure the new model directory `model/exported/model_v1.0.1/` is synced and verified.
2. Run the deployment script with the new target version:
   ```bash
   ./deploy.sh v1.0.1
   ```
3. The script will:
   - Build/pull image tagged `v1.0.1`
   - Restart the containers with updated environment parameters
   - Poll `/api/v1/health` until all services report `"healthy"`

---

## 6. Emergency Rollback Strategy

If a newly deployed release regresses in performance, throws unexpected validation errors, or fails health checks:

### Automated Rollback Command:
```bash
cd /opt/pd-voice/deployment/production
./rollback.sh v1.0.0
```

### Rollback Lifecycle:
1. Instantly points Docker Compose back to image tags `pd-voice-backend:v1.0.0` and `pd-voice-frontend:v1.0.0`.
2. Sets `MODEL_VERSION=model_v1.0.0` without rebuilding containers.
3. Restarts the containers in `< 5 seconds`.
4. Performs automated health verification against `/api/v1/health`.

---

## 7. Production Monitoring & Health Alerting

Configure uptime monitoring (e.g., Datadog, Prometheus/Grafana, or Uptime Kuma) to ping:
- **Endpoint**: `GET /api/v1/health`
- **Interval**: 15 seconds
- **Alert Condition**: HTTP status $\neq 200$ OR JSON `status != "healthy"` OR `services.database != "connected"`.
