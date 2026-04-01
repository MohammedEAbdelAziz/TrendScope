# TrendScope

TrendScope is a full-stack economic sentiment monitoring platform. It collects financial headlines, classifies sentiment with an ONNX-optimized model, and exposes regional trend data through an API and web dashboard.

## Overview

The platform tracks sentiment across seven regions:

- Global
- United States
- European Union
- Africa
- Egypt
- Saudi Arabia
- Middle East

Headline collection is scheduled with Celery Beat, and results are persisted for trend analysis and historical comparison.

## Architecture

- Backend: FastAPI, Celery, Redis, SQLite
- Sentiment inference: Distilled FinancialBERT exported to ONNX (quantized)
- Frontend: SvelteKit
- Deployment: Docker Compose

## Repository Layout

- backend: API, workers, model tooling, and data pipeline
- frontend: SvelteKit dashboard and API proxy routes
- docker-compose.yml: local and server orchestration

## Quick Start (Docker)

From repository root:

```bash
docker compose up --build
```

This compose setup is production-oriented:

- Frontend is intended to be exposed by reverse proxy (Traefik/Coolify).
- Backend, Redis, and Celery services are internal-only.

## Development Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Model Build and Dependencies

This repository separates runtime and model-build dependencies.

- Runtime dependencies: backend/requirements.txt
- Model build/export dependencies: backend/requirements.model-build.txt

Use the model-build set only when rebuilding ONNX artifacts:

```bash
cd backend
pip install -r requirements.model-build.txt
python build_model.py
```

Note: model build dependencies may be significantly heavier than runtime dependencies.

## Health Checks and Operations

Use liveness endpoints for orchestrator health decisions:

- Frontend liveness: /healthz or /health (port 3000)
- Backend liveness: /health, /healthz, or /health/live (port 8000)

Readiness diagnostics:

- Backend readiness: /health/ready or /api/health

Quick checks after deployment:

```bash
# External check (replace with your domain)
curl -i https://your-domain.example/healthz

# Internal container checks
docker compose exec frontend wget -q -O - http://localhost:3000/healthz
docker compose exec backend curl -i http://localhost:8000/health/live
docker compose exec backend curl -i http://localhost:8000/health/ready
```

## Coolify Notes

- Assign your domain to the frontend service in Coolify.
- Set the service port to 3000 in the domain configuration.
- Do not expose backend/redis/celery services with domains or host ports.
- Keep frontend health check path at /healthz.

## Troubleshooting Gateway Timeouts

If health appears green but the domain still times out, validate service reachability through the proxy path:

```bash
docker compose ps
docker compose logs --tail=200 frontend
docker compose logs --tail=200 backend
curl -i https://your-domain.example/
curl -i https://your-domain.example/healthz
```

In this situation, the common root cause is reverse-proxy networking/routing, not application liveness.

## License

MIT. See LICENSE for details.
