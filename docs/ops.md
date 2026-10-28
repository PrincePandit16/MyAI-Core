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

- **Database**: Schedule daily snapshots of the PostgreSQL instance.
- **Vector Store**: Use Milvus backup tools to snapshot the collection.
- **Recovery**: In case of failure, restore the latest DB snapshot and re-index documents from the source connectors.
