# Security & Privacy Hardening Guide

This document outlines the security posture, secret management, and privacy guidelines for the AI Assistant project.

## 1. Secrets Management

### Current State
Secrets are currently managed via `.env` files and environment variables.

### Recommended Hardening
For production environments, move away from static `.env` files to a dedicated Secret Manager:
- **HashiCorp Vault**: Use the KV (Key-Value) store for application secrets.
- **Cloud Secret Managers**: 
  - AWS Secrets Manager
  - Azure Key Vault
  - Google Secret Manager

### Implementation Guidelines
1. **Injection**: Prefer injecting secrets as environment variables at runtime (e.g., via Kubernetes Secrets or Vault Agent) rather than reading files.
2. **Rotation**: Implement token rotation for `jwt_secret_key` and API keys (`groq_api_key`, `milvus_token`).
3. **Least Privilege**: Use different API keys for development, staging, and production environments.

## 2. Data Privacy & Encryption

### Vector Store & Document Storage
- **Encryption at Rest**: Ensure the underlying storage for FAISS/Milvus is encrypted.
- **Transport Encryption**: Use TLS/SSL for all connections to the database and vector store (`milvus_uri` should use `https`).
- **Data Isolation**: Implement tenant-level isolation if the system expands to support multiple users with private document sets.

### Logging & Telemetry
- **Redaction**: Sensitive data (Passwords, JWTs, PII) must be redacted from logs.
- **Telemetry**: User telemetry is opt-in. Only aggregated, anonymized usage metrics are collected.

## 3. Security Checklist

- [ ] All API endpoints are protected by JWT authentication.
- [ ] `jwt_secret_key` is a high-entropy random string (not hardcoded).
- [ ] Database and Vector Store connections use TLS.
- [ ] PII is redacted from application logs.
- [ ] Dependency vulnerabilities are scanned (e.g., via `pip-audit` or `npm audit`).
- [ ] CORS policies are restrictive and avoid `*`.

## 4. Incident Response Runbook

### Detection
- Monitor Prometheus metrics for spikes in `5xx` errors or unusual request volume.
- Check logs for repeated `401 Unauthorized` or `403 Forbidden` errors (potential brute force).

### Containment
1. **Credential Leak**: 
   - Rotate the leaked secret immediately in the Secret Manager.
   - Restart the application to pick up new secrets.
   - Invalidate all active JWT sessions by rotating the `jwt_secret_key`.
2. **Service Compromise**:
   - Isolate the affected container/node.
   - Revoke API keys associated with the compromised environment.

### Recovery
- Restore from the last known clean backup if data was corrupted.
- Audit logs to determine the extent of the breach.
- Notify affected users if PII was compromised.
