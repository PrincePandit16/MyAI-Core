# Personal AI Assistant

A local-development starter for a personal AI assistant, with a FastAPI backend, a React + Vite + TypeScript frontend, and vector search integrations for FAISS and Milvus.

## Run locally

Prerequisites: Docker with the Compose plugin.

To run the backend directly during development:

```sh
uv sync --project backend
uv run --project backend uvicorn app.main:app --reload
```

From the repository root:

```sh
docker compose -f infra/docker-compose.yml up --build
```

- Frontend: http://localhost:5173
- Backend health check: http://localhost:8000/health
- FAISS runs as a library inside the backend container; Milvus runs as a separate service.
- The chat endpoint forwards prompts to the configured language model. Chat messages are not persisted.

### Document embeddings and search

The backend can embed Markdown documents with
`sentence-transformers/all-MiniLM-L6-v2` and store them in a Milvus collection.
Install the backend dependencies with `uv sync --project backend` and make a
Milvus server available at
`http://localhost:19530` (or set `MILVUS_URI` to your server address). The
optional `MILVUS_TOKEN` is used for authenticated Milvus servers.

From the repository root, index Markdown files recursively:

```powershell
uv run --project backend python backend\scripts\index_docs.py path\to\markdown
```

The script loads `backend/.env` and supports `EMBEDDING_MODEL_NAME`,
`MILVUS_URI`, `MILVUS_TOKEN`, and `MILVUS_COLLECTION_NAME`. Long Markdown files
are split into chunks before embedding. In Python, use `EmbeddingService.embed`
to encode a query and `VectorStore.query(embedding, top_k=5)` to retrieve
matching `SearchResult` records.

### Language model setup

The backend supports three providers: `http_tgi`, `local_llama`, and the
existing `groq` provider. Set `LLM_MODE` and the provider settings in
`backend/.env` (see [`backend/.env.example`](backend/.env.example)). Do not
replace an existing `.env` file just to apply the example; add or change only
the settings you need. Changes to environment settings require restarting the
backend.

#### Hugging Face TGI

Start a TGI server using the
[official TGI documentation](https://huggingface.co/docs/text-generation-inference/index).
For example, on a Linux host with NVIDIA Container Toolkit and Docker:

```sh
model=HuggingFaceH4/zephyr-7b-beta
docker run --gpus all --shm-size 1g -p 8080:80 \
  -v "$HOME/.cache/huggingface:/data" \
  ghcr.io/huggingface/text-generation-inference:3.3.5 \
  --model-id "$model"
```

For a backend running directly on the host, configure:

```dotenv
LLM_MODE=http_tgi
TGI_ENDPOINT=http://localhost:8080/generate
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=3
LLM_MAX_NEW_TOKENS=256
```

For the Compose backend, TGI is expected to be running on the Docker host.
Compose defaults to `http://host.docker.internal:8080/generate`; override
`TGI_ENDPOINT` if TGI is elsewhere. Start the application from the repository
root:

```powershell
$env:LLM_MODE = "http_tgi"
$env:TGI_ENDPOINT = "http://host.docker.internal:8080/generate"
docker compose -f infra/docker-compose.yml up --build
```

Test TGI directly:

```powershell
curl.exe -X POST http://localhost:8080/generate `
  -H "Content-Type: application/json" `
  -d '{"inputs":"Say hello","parameters":{"max_new_tokens":64}}'
```

#### Local llama.cpp

Build/install a llama.cpp CLI binary by following the
[llama.cpp build instructions](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)
and download a compatible GGUF model. The binary and model must be accessible
to the backend process. For example, configure `backend/.env` for a Windows
host with:

```dotenv
LLM_MODE=local_llama
LLAMA_BINARY_PATH=C:\path\to\llama.cpp\build\bin\Release\llama-cli.exe
LLAMA_MODEL_PATH=C:\path\to\models\model.gguf
LLM_TIMEOUT_SECONDS=60
LLM_MAX_NEW_TOKENS=256
```

The Windows build can be created from a Visual Studio Developer PowerShell:

```powershell
git clone https://github.com/ggml-org/llama.cpp.git
Set-Location llama.cpp
cmake -B build
cmake --build build --config Release
```

Set `LLAMA_BINARY_PATH` to the resulting `llama-cli.exe`, set
`LLAMA_MODEL_PATH` to the downloaded GGUF model, and run the backend from
`backend/`:

```powershell
$env:LLM_MODE = "local_llama"
$env:LLAMA_BINARY_PATH = "C:\path\to\llama.cpp\build\bin\Release\llama-cli.exe"
$env:LLAMA_MODEL_PATH = "C:\path\to\models\model.gguf"
uv run --project backend python -m uvicorn app.main:app --reload
```

This provider launches llama.cpp for one turn per request with a configured
generation limit and no prompt echo; there is no separate llama.cpp server to
start for this mode. On Linux or macOS, build the corresponding binary and use
its binary/model paths.
The standard Compose backend image does not bundle llama.cpp or a model; use a
custom image that includes them and set `LLAMA_BINARY_PATH` and
`LLAMA_MODEL_PATH` to paths inside that container if running this mode in
Compose.

#### Test chat through the backend

With the backend running and a provider available, send a request:

```powershell
curl.exe -X POST http://localhost:8000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"session_id":"phase6-test","prompt":"Say hello"}'
```

The response contains the model output in `response`. Provider failures return
HTTP 502 rather than a success-shaped chat response. To test a real configured
provider from the repository root, run:

```powershell
uv run --project backend python backend\scripts\test_llm_client.py
```

Automated adapter and route tests can be run with:

```powershell
uv run --project backend --group dev pytest backend/tests -q
```

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
`uv sync --project backend`):

```sh
uv run --project backend python -m alembic upgrade head
```

To create or regenerate a migration after changing models, use:

```sh
uv run --project backend python -m alembic revision --autogenerate -m "create users and sessions"
uv run --project backend python -m alembic upgrade head
```

The default local connection is
`postgresql+psycopg://assistant:assistant@localhost:5432/assistant`; override it
with the `DATABASE_URL` environment variable when needed. When the backend is
running in Compose, it connects to the `postgres` service automatically.

Create a user interactively from `backend/` after upgrading the database:

```sh
uv run --project backend python -m scripts.create_user
```

The script prompts for an email and password and stores only the Argon2 password
hash.

To remove one disposable test user and that user's assistant sessions, run this
from `backend/` and confirm the exact email when prompted:

```sh
uv run --project backend python -m scripts.delete_user
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
