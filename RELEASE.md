# Release Notes

This document outlines the steps for releasing the AI Assistant to production.

## Release Version: v0.1.0 (MVP)

### Deployment Checklist

- [ ] **Infrastructure**: K8s cluster provisioned and configured.
- [ ] **Database**: PostgreSQL instance running and accessible.
- [ ] **Vector Store**: Milvus standalone or cluster deployed.
- [ ] **Secrets**: `.env` production variables configured in K8s Secrets.
- [ ] **Build**: Frontend and Backend Docker images pushed to registry.

### Deployment Steps

#### 1. Database Migration
Run the Alembic migrations against the production database:
```bash
uv run --project backend python -m alembic upgrade head
```

#### 2. Backend Deployment
Deploy the backend pods:
```bash
kubectl apply -f infra/k8s/backend-deployment.yaml
```

#### 3. Frontend Deployment
Deploy the frontend assets to the production web server:
```bash
# Example for static hosting
npm run build
scp -r dist/* user@prod-server:/var/www/html
```

#### 4. Smoke Testing
Verify the following:
- [ ] `/health` endpoint returns 200 OK.
- [ ] User can register and log in.
- [ ] Chat responses are generated successfully.
- [ ] Metrics are flowing into Prometheus.

## Rollback Plan

If a critical issue is detected after deployment:
1. **Backend**: Roll back to the previous image version using `kubectl rollout undo deployment/backend`.
2. **Database**: Restore the PostgreSQL snapshot taken immediately before deployment.
3. **Frontend**: Revert to the previous build version on the web server.
