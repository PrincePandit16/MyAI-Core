# Developer Guide

This guide helps new contributors get the project running locally and understand how to extend the system.

## Prerequisites

- **Docker & Docker Compose**: For running the full stack.
- **Python 3.11+**: For local backend development.
- **Node.js & npm**: For frontend development.
- **uv**: Fast Python package manager (recommended).

## Quick Start (Full Stack)

The easiest way to start the project is using Docker Compose.

```bash
# Start all services (Backend, Frontend, Postgres, Milvus)
docker compose -f infra/docker-compose.yml up --build
```

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

## Local Development

### Backend
1. **Install dependencies**:
   ```bash
   uv sync --project backend --group dev
   ```
2. **Set up environment**:
   Copy `.env.example` to `.env` and update the values.
3. **Run migrations**:
   ```bash
   uv run --project backend python -m alembic upgrade head
   ```
4. **Start the server**:
   ```bash
   uv run --project backend uvicorn app.main:app --reload
   ```

### Frontend
1. **Install dependencies**:
   ```bash
   cd frontend && npm install
   ```
2. **Start dev server**:
   ```bash
   npm run dev
   ```

## Extending the System

### Adding New Connectors
To add a new data source (e.g., Notion, Google Drive):
1. Create a new connector class in `backend/app/connectors/`.
2. Implement the `fetch_documents()` method to retrieve data.
3. Add the connector to the ingestion pipeline to embed and store documents in Milvus.

### Swapping Vector Stores (e.g., Milvus $\rightarrow$ Weaviate)
The backend uses a service layer to abstract vector operations.
1. Create a new implementation of the vector store interface in `backend/app/services/vector_store.py`.
2. Update the `settings.py` to include Weaviate configuration.
3. Update the factory method in the vector store service to return the Weaviate client based on the configuration.

## Testing

- **Run Backend Tests**:
  ```bash
  uv run --project backend pytest
  ```
- **Run Specific Test**:
  ```bash
  uv run --project backend pytest backend/tests/test_file.py
  ```
