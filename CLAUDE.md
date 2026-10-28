# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
- **Install dependencies**: `uv sync --project backend --group dev`
- **Run server**: `uv run --project backend uvicorn app.main:app --reload`
- **Run all tests**: `uv run --project backend pytest`
- **Run single test**: `uv run --project backend pytest backend/tests/test_file.py`
- **DB Migrations**:
  - Upgrade: `uv run --project backend python -m alembic upgrade head`
  - Autogenerate: `uv run --project backend python -m alembic revision --autogenerate -m "message"`
- **User Management**:
  - Create user: `uv run --project backend python -m scripts.create_user`
  - Delete user: `uv run --project backend python -m scripts.delete_user`

### Frontend (React + Vite + TS)
- **Install dependencies**: `cd frontend && npm install`
- **Run dev server**: `cd frontend && npm run dev`
- **Build**: `cd frontend && npm run build`

### Infrastructure (Docker)
- **Start full stack**: `docker compose -f infra/docker-compose.yml up --build`
- **Start with Redis**: `docker compose -f infra/docker-compose.yml --profile data up --build`
- **Start with Proxy**: `docker compose -f infra/docker-compose.yml --profile proxy up --build`
- **Stop and remove**: `docker compose -f infra/docker-compose.yml down` (add `-v` to delete DB volumes)

## Architecture

### High-Level Structure
The project is a decoupled client-server application:
- `backend/`: A FastAPI application providing the AI assistant logic and data persistence.
- `frontend/`: A React frontend built with Vite, TypeScript, and Tailwind CSS.
- `infra/`: Docker Compose configurations for local orchestration.

### Backend Architecture
The backend follows a layered pattern for separation of concerns:
- `app/main.py`: Entry point and API route definitions.
- `app/models/`: SQLAlchemy models defining the database schema (Users, Sessions).
- `app/crud/`: Create, Read, Update, Delete operations for data access logic.
- `app/db/`: Database session management and connectivity.
- `app/core/`: Application-wide configuration and settings.
- `migrations/`: Alembic version scripts for database schema evolution.

### Data Storage
- **PostgreSQL**: Primary relational storage for users and sessions.
- **FAISS**: Integrated as a library within the backend for single-node vector search.
- **Redis**: Optional caching/messaging layer (enabled via `--profile data`).
