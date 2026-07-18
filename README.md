# Personal OS

A modular, self-hosted productivity platform. This repository contains a React frontend and FastAPI backend, with Docker services for PostgreSQL, Redis, Meilisearch, and MinIO.

## Start locally

1. Install Node 20+ and Python 3.11+.
2. Copy `backend/.env.example` to `backend/.env`.
3. Run infrastructure: `docker compose up -d postgres redis meilisearch minio`.
4. Backend: `cd backend; python -m venv .venv; .venv\\Scripts\\pip install -r requirements.txt; .venv\\Scripts\\uvicorn app.main:app --reload`.
5. Frontend: `cd frontend; npm install; npm run dev`.

The frontend is served at `http://localhost:5173`; the API docs are at `http://localhost:8000/docs`.

## Architecture

- `frontend/` — React, TypeScript, Tailwind interface and modular navigation.
- `backend/` — FastAPI API, SQLAlchemy models, JWT-ready configuration.
- Docker Compose — local PostgreSQL, Redis, Meilisearch, and S3-compatible MinIO.

New product areas should be added as a frontend feature and a matching backend router, keeping modules independent while sharing authentication, search, files, and events.
