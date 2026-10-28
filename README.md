# Personal AI Assistant

A local-development starter for a personal AI assistant, with a FastAPI backend, a React + Vite + TypeScript frontend, and vector search integrations for FAISS and Milvus.

## 🚀 Quick Start

The fastest way to get the entire system running is using Docker Compose:

```sh
docker compose -f infra/docker-compose.yml up --build
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📖 Documentation

For detailed guides, please refer to the `/docs` directory:
- [Architecture](docs/architecture.md) - High-level system design and data flow.
- [Developer Guide](docs/dev-guide.md) - Local setup, extending connectors, and testing.
- [Operations Guide](docs/ops.md) - Deployment, monitoring, and backup strategies.
- [MVP Guide](docs/README_MVP.md) - Step-by-step instructions for first-time users.

## 🛠️ Technical Overview

### Core Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic.
- **Frontend**: React, TypeScript, Tailwind CSS, Vite.
- **Database**: PostgreSQL for user and session data.
- **Vector Search**: Milvus (standalone) or FAISS (library).
- **LLM Support**: Local llama.cpp, Hugging Face TGI, or Groq.

### Document Indexing
The backend can embed Markdown documents and store them in a Milvus collection.
To index documents from the repository root:
```powershell
uv run --project backend python backend\scripts\index_docs.py path\to\markdown
```

### Language Model Setup
The backend supports multiple providers. Configure `LLM_MODE` in `backend/.env` (see `backend/.env.example`):
- `http_tgi`: Connects to a Hugging Face TGI server.
- `local_llama`: Executes `llama-cli` locally.
- `groq`: Uses the Groq Cloud API.

## 📁 Project Layout

- `backend/` — FastAPI service, RAG logic, and tests.
- `frontend/` — React application.
- `infra/` — Docker Compose and Kubernetes configurations.
- `docs/` — Comprehensive system documentation.
