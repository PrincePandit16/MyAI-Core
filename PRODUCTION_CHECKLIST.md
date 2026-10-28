# Production Readiness Checklist

## 🛡️ Security & TLS
- [ ] **TLS/SSL**: Implement TLS for all public endpoints using Traefik or a Cloud Load Balancer.
- [ ] **Secret Management**: Move environment variables to a secure vault (e.g., HashiCorp Vault, AWS Secrets Manager, Kubernetes Secrets).
- [ ] **JWT Secret**: Rotate `JWT_SECRET` and ensure it is a high-entropy string.
- [ ] **Database Access**: Restrict PostgreSQL access to only the backend service (no public 5432).
- [ ] **CORS**: Configure strict CORS policies in FastAPI to allow only the official frontend domain.

## 💾 Data Persistence & Backup
- [ ] **DB Backups**: Set up automated `pg_dump` cron jobs to an S3-compatible bucket.
- [ ] **Vector Store Backup**: Implement backup strategy for Milvus data volumes.
- [ ] **Volume Persistence**: Ensure K8s PersistentVolumeClaims (PVCs) are backed by durable storage (e.g., EBS, Azure Disk).

## 📈 Observability
- [ ] **Alerting**: Configure Prometheus Alertmanager for critical failures (e.g., 5xx error spikes).
- [ ] **Logging**: Aggregate logs using an EFK/ELK stack or Grafana Loki.
- [ ] **Health Checks**: Ensure K8s Liveness and Readiness probes are correctly configured.

## 🚀 Deployment
- [ ] **Resource Limits**: Set CPU/Memory requests and limits for all containers.
- [ ] **Horizontal Scaling**: Configure HPA (Horizontal Pod Autoscaler) for the backend based on CPU/Memory.
- [ ] **Graceful Shutdown**: Ensure FastAPI handles `SIGTERM` for zero-downtime deployments.
