# Operations Guide

This document describes the deployment and operational management of the AI Assistant.

## Deployment Architecture

For production, the system is designed to be deployed on Kubernetes (K8s) or a similar container orchestrator.

### Production Components
- **API Gateway**: Traefik or Nginx for SSL termination and load balancing.
- **App Servers**: Multiple replicas of the FastAPI backend.
- **Frontend**: Static files served via Nginx or a CDN.
- **Managed Database**: PostgreSQL (e.g., AWS RDS, GCP Cloud SQL).
- **Managed Vector Store**: Milvus Cluster or Weaviate Cloud.
- **Monitoring**: Prometheus and Grafana deployed as a sidecar or central cluster.

## Deployment Steps

1. **Infrastructure Setup**:
   - Provision K8s cluster.
   - Setup PostgreSQL and Milvus instances.
   - Configure secrets (JWT keys, DB passwords, API keys).

2. **Backend Deployment**:
   - Build Docker image and push to registry.
   - Apply K8s manifests (`infra/k8s/backend-deployment.yaml`).
   - Run DB migrations using an InitContainer or a CI/CD job.

3. **Frontend Deployment**:
   - Build production assets: `npm run build`.
   - Deploy to static hosting or K8s pod with Nginx.

4. **Verification**:
   - Check `/health` endpoint of the backend.
   - Verify connectivity to the vector store and database.

## Monitoring & Alerting

### Key Metrics to Watch
- **Request Latency**: Monitor `llm_response_seconds` to ensure the LLM provider is performing within limits.
- **Error Rates**: Track `http_requests_total` filtered by `http_status=502` or `500`.
- **Resource Usage**: Monitor CPU/Memory of the FastAPI pods.

### Log Management
- Logs are redacted via `RedactingFormatter` to prevent leaking PII or secrets.
- Logs should be aggregated using a tool like EFK (Elasticsearch, Fluentd, Kibana) or Loki.

## Backup & Recovery

- **Database**: Schedule daily snapshots of PostgreSQL. The example Kubernetes CronJob writes to an encrypted PVC, but production operators must copy backups to encrypted object storage with lifecycle retention and separate credentials.
- **Vector Store**: Use Milvus backup tooling and store backups with encryption at rest.
- **Restore testing**: Run a restore drill monthly and verify application tests against restored data.
- **Recovery objective**: Document and monitor the RPO/RTO. Do not claim a target until restore tests demonstrate it.

## Production Release Checklist

- Replace every `example.com`, `OWNER`, and `RELEASE_TAG` placeholder.
- Supply `JWT_SECRET_KEY`, database credentials, MinIO credentials, and provider API keys from an external secret manager.
- Terminate TLS at Traefik or an ingress controller and configure HTTP-to-HTTPS redirect.
- Use immutable image tags or digests and verify signatures in admission policy.
- Enable network policies and encrypted storage classes in the Kubernetes cluster.
- Configure centralized logs, metrics, alerts, backup retention, and incident on-call routing.
- Run dependency, secret, SAST, container, and API security scans before every release.
- Rotate credentials, verify MFA for privileged accounts, and run restore exercises.
- Keep `COOKIE_SECURE=true`; secure cookies require HTTPS in production.

## Secret and TLS Bootstrap

```sh
kubectl create secret generic backend-secrets \
  --from-literal=database_url='postgresql+psycopg://USER:PASSWORD@postgres:5432/assistant' \
  --from-literal=jwt_secret_key="$(openssl rand -base64 48)"

kubectl create secret tls ai-assistant-tls \
  --cert=/secure/path/tls.crt --key=/secure/path/tls.key
```
