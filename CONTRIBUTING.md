# Contributing

Thanks for contributing. Please open an issue for significant changes before starting work, and keep pull requests focused.

## Development checks

- Backend: create an environment with `uv venv backend/.venv`, install test dependencies with `uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements-dev.txt` on Windows (use `backend/.venv/bin/python` on Unix), then run `pytest backend/tests`.
- Frontend: from `frontend/`, run `npm install` and `npm run build`.
- Local stack: from the repository root, run `docker compose -f infra/docker-compose.yml up --build`.

Add or update tests for behavior changes. Ensure the CI checks pass before requesting review.

## Code style

- Python: follow PEP 8, use type annotations for new public functions, and keep API behavior explicit.
- TypeScript/React: use strict TypeScript, functional components, and the existing formatting and Tailwind conventions.
- Keep secrets and machine-specific configuration out of committed files; use environment variables for local overrides.

## Pull requests

Include a concise summary, link related issues, and note the tests or build checks you ran.
