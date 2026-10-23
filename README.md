# Personal AI Assistant

A local-development starter for a personal AI assistant, with a FastAPI backend, a React + Vite + TypeScript frontend, and FAISS available in the backend for single-node vector search.

## Run locally

Prerequisites: Docker with the Compose plugin.

To run the backend directly during development:

```sh
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

From the repository root:

```sh
docker compose -f infra/docker-compose.yml up --build
```

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health
- FAISS runs as a library inside the backend container; it does not need a separate service.
- The frontend chat form can test the connection to the backend. The current chat endpoint echoes the submitted message and does not save chat messages or create users.

PostgreSQL starts with the default Compose stack. Start Redis (an optional service) with:

```sh
docker compose -f infra/docker-compose.yml --profile data up --build
```

### Database migrations and creating a user

When running the backend directly, start PostgreSQL from the repository root:

```sh
docker compose -f infra/docker-compose.yml up -d postgres
```

Then run migrations from `backend/` (install dependencies first with
`pip install -r requirements.txt`):

```sh
python -m alembic upgrade head
```

To create or regenerate a migration after changing models, use:

```sh
python -m alembic revision --autogenerate -m "create users and sessions"
python -m alembic upgrade head
```

The default local connection is
`postgresql+psycopg://assistant:assistant@localhost:5432/assistant`; override it
with the `DATABASE_URL` environment variable when needed. When the backend is
running in Compose, it connects to the `postgres` service automatically.

Create a user interactively from `backend/` after upgrading the database:

```sh
python -m scripts.create_user
```

The script prompts for an email and password and stores only the Argon2 password
hash.

To remove one disposable test user and that user's assistant sessions, run this
from `backend/` and confirm the exact email when prompted:

```sh
python -m scripts.delete_user
```

This targets only the email you enter; it does not clear other users or remove
the database volume. The frontend chat test does not create database records.

### MVP authentication

Register with `POST /auth/register` and log in with `POST /auth/login`, using
JSON bodies containing `email` and `password`. Login returns a bearer access
token; send it in the `Authorization` header to access `GET /auth/me`.
Registration and login use bcrypt hashes; users created by the existing
management script with Argon2 hashes can also log in.

Set `JWT_SECRET_KEY` to a stable, secret value before deploying or running more
than one backend process. If it is not set, a random key is generated at startup,
so existing tokens stop working when the process restarts.

Later replace this with Ory Kratos integration — migration plan: map Kratos
identities to our User table.

Start the Traefik stub with the `proxy` profile:

```sh
docker compose -f infra/docker-compose.yml --profile proxy up --build
```

Stop the services with `Ctrl+C`; run `docker compose -f infra/docker-compose.yml down` to remove the containers. Add `-v` to that command to also delete the PostgreSQL data volume.

## Project layout

- `backend/` — FastAPI service and tests
- `frontend/` — React, Vite, TypeScript, and Tailwind CSS
- `infra/` — local Docker Compose configuration
