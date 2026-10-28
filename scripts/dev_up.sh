#!/bin/bash
set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "🚀 Starting the stack..."
docker compose -f infra/docker-compose.yml up --build -d

echo "⏳ Waiting for services to be healthy..."

# Wait for Postgres
until docker compose -f infra/docker-compose.yml exec postgres pg_isready -U assistant; do
  echo "Waiting for Postgres..."
  sleep 2
done

echo "✅ All services are up!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
docker compose -f infra/docker-compose.yml logs -f
