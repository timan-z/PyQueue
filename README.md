# PyQueue (FastAPI) — Task Queue Backend + Minimal React Dashboard

PyQueue is a Python/FastAPI implementation of a small, educational **job/task queue** inspired by production systems like **Celery** and **Sidekiq**. It is part of my “Queue” project series—each project implements the same core producer/consumer task-queue idea in a different ecosystem to build deep, comparative backend intuition.

This repo is structured as a **monorepo** with:
- a FastAPI backend (`/PyQueue-Backend`)
- a lightweight React + TypeScript + Vite dashboard (`/PyQueue-Frontend`)

> **Backend-first philosophy:** the backend is the source of truth. The frontend is intentionally thin and adapts to the backend contract (schemas, enums, request/response shapes).

---

## Project Lineage (Why PyQueue exists)

PyQueue sits in a larger sequence of queue systems:

- **GoQueue** — a minimal Go-based queue implementation + dashboard (early “core ideas” phase)
- **SpringQueue (base)** — a Java/Spring Boot version that focuses on REST + DI fundamentals
- **SpringQueuePro** — a production-oriented Spring ecosystem build (persistence, infra-heavy patterns, etc.)
- **PyQueue (this repo)** — translates the same architecture into the Python ecosystem using **FastAPI**, with explicit API contracts and clean dependency wiring

PyQueue is *not* a copy-paste port. It is intentionally designed to highlight how:
- dependency injection differs between Spring and FastAPI
- concurrency primitives differ across Go / Java / Python
- API contracts benefit from explicit schema boundaries
- a “backend-first” contract keeps clients honest and stable

---

## What PyQueue does

### Backend capabilities (FastAPI)
- **Enqueue tasks** with a payload + task type
- **Process tasks asynchronously** using a worker pool (thread pool)
- **Track task lifecycle** in an in-memory registry
- **Retry failed tasks** (both automatic retry logic and manual retry endpoint)
- **Inspect tasks** (list all, fetch by id, view metadata such as attempts/max retries)
- **Delete tasks** and **clear the queue**

### Frontend capabilities (React dashboard)
A minimal dashboard to:
- enqueue new tasks
- list all tasks
- inspect a selected task (including attempts/max retries and timestamp)
- delete a task
- retry failed tasks
- clear the job list

The frontend is intentionally simple and UI-focused; deeper details live in backend docs and code.

---

## Architecture overview

PyQueue implements a classic **Producer–Consumer** model:

- **Producer (API layer):**
  - accepts enqueue requests
  - creates tasks via a single factory (`Task.create(...)`)
  - registers tasks with the queue service

- **Queue (coordination service):**
  - owns the task registry (`jobs`)
  - owns the thread pool executor (worker pool)
  - owns lock-protected access to shared state
  - submits work via a `worker_factory(...)` (dependency injection-friendly)

- **Worker (execution unit):**
  - processes a single task attempt
  - updates task status (`QUEUED → INPROGRESS → COMPLETED/FAILED`)
  - may re-enqueue if retry rules allow

- **Schemas (API contract):**
  - internal models use internal field names (`t_id`, `t_type`, etc.)
  - API schemas expose clean external DTOs (`id`, `type`, etc.)
  - explicit mapping occurs in `schemas/mappers.py`

---

## Repository structure

```
/PyQueue-Backend
- /enums
-- TaskStatus.py
-- TaskType.py
- /models
-- task.py
-- queue.py
- /schemas
-- task.py
-- mappers.py
- /system
-- producer.py
-- worker.py
- main.py
/PyQueue-Frontend
- /src
-- /components
--- JobsList.tsx
--- JobDisplay.tsx
--- LoadingSpinner.tsx
-- /utility
--- api.ts
--- types.ts
App.tsx
App.css
main.tsx
```

---

## API contract (Backend)

### TaskType
PyQueue uses explicit enum values (string enums) for API-facing stability:

- `EMAIL`
- `REPORT`
- `DATACLEANUP`
- `SMS`
- `NEWSLETTER`
- `TAKESLONG`
- `FAIL`
- `FAILABS`
- `TEST`

### TaskStatus
- `QUEUED`
- `INPROGRESS`
- `COMPLETED`
- `FAILED`

### TaskResponse (public DTO)
The backend exposes execution metadata for inspection (useful for future PyQueuePro UI):

```json
{
  "id": "Task-123...",
  "payload": "hello",
  "type": "EMAIL",
  "status": "QUEUED",
  "attempts": 0,
  "max_retries": 3,
  "created_at": "2026-02-03T15:34:21.123456"
}
````

---

## Frontend ↔ Backend integration notes (important)

This project intentionally keeps a strict boundary:

* **Backend defines meaning:** request keys, enum vocabulary, schema shape
* **Frontend adapts:** maps UI-friendly labels to backend enums, reads snake_case fields, formats timestamps only at render time

Key adaptations from the GoQueue / SpringQueue template:

* `types.ts` reflects the exact FastAPI DTO (snake_case, ISO strings)
* `api.ts` maps UI dropdown values (e.g. `"fail-absolute"`) → backend enum values (`"FAILABS"`)
* status checks use backend vocabulary (`"FAILED"`, not `"failed"`)
* timestamps are formatted only in components (presentation layer), not reshaped at the API boundary

For deeper details, see:

* **Phase 4 – Frontend Integration** doc (and earlier phase notes)

---

## Running locally

### 1) Backend (FastAPI)

From `/PyQueue-Backend`:

```bash
# create / activate your venv (example)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at:

* `http://127.0.0.1:8000`

---

### 2) Frontend (Vite + React + TS)

From `/PyQueue-Frontend`:

```bash
npm install
npm run dev
```

Frontend runs at:

* `http://localhost:5173`

---

## Environment variables

### Frontend (Netlify / Vite)

The frontend reads the backend base URL via Vite env vars:

`.env` (frontend):

```
VITE_API_BASE=http://127.0.0.1:8000
```

In code:

```ts
const API_BASE = import.meta.env.VITE_API_BASE.replace(/\/+$/, "");
```

---

### Backend (Railway / FastAPI)

The backend uses environment variables primarily for **CORS origin configuration** (and later, additional production settings).

Example backend `.env`:

```
FRONTEND_ORIGIN=http://localhost:5173
```

At runtime, configure CORS with `FRONTEND_ORIGIN` (or multiple origins via a comma-separated list).

---

## Deployment

Typical deployment setup:

* **Backend:** Railway
* **Frontend:** Netlify

In production:

* Netlify sets `VITE_API_BASE` to the Railway backend URL
* Railway sets `FRONTEND_ORIGIN` to the Netlify frontend URL

(See Phase-specific docs for deployment notes and common pitfalls.)

---

## Phase documentation

This repo is structured around phases, each with its own learning goals and design decisions:

* **[Phase 1](./additional_docs/phase-1-translation-notes.md):** Core queue design + concurrency translation (from GoQueue *and* SpringQueue)
* **[Phase 2](./additional_docs/phase-2-fastapi-integration.md):** FastAPI integration + API shaping + enums
* **[Phase 3](./additional_docs/phase-3-dependency-injection-refactoring.md):** Code smell fixes + FastAPI dependency injection wiring + factory injection
* **[Phase 4](./additional_docs/phase-4-frontend-integration.md):** Frontend integration (React dashboard) + env vars + DTO alignment
* **[Phase 4.5](./additional_docs/phase-4-part-2-netlify-railway-deployment.md)**: Miscellaneous Railway and Netlify deployment details

Each phase document captures the “why,” not just the “what.”<br>
(***See `additional_docs` folder for documentation on each explicit Phase...***).

---

## Key design decisions (high-level)

### 1) Internal models vs API schemas

Internal model fields (`t_id`, `t_type`) remain internal to preserve clarity and flexibility.
API schemas expose the stable contract (`id`, `type`) consumed by clients.

### 2) String enums, not `auto()`

Enums used for API-facing values are string enums to keep:

* OpenAPI docs readable
* client implementations straightforward
* contract stable and explicit

### 3) Worker factory injection (dependency direction)

Instead of hard-importing Worker inside the queue, the queue accepts a `worker_factory`.
This reduces circular dependencies and mirrors constructor injection patterns (Spring-style) in a Pythonic way.

### 4) “Backend-first” frontend

The dashboard is an adapter, not an authority.
No implicit casing conversions, no invented fields, no “best guess” semantics.

---

## Future work / What’s next

### PyQueuePro (FastAPI ecosystem mirror of SpringQueuePro)

A future “Pro” edition mirroring the goals of SpringQueuePro, but in Python/FastAPI:

* persistence (PostgreSQL)
* task history / auditing
* metrics / tracing
* richer admin UI (filtering, detail inspection, dashboards)
* potentially distributed coordination concepts (as applicable in Python ecosystem)

### DjangoQueue + FlaskQueue (framework comparison projects)

Two “splinter” projects built from the same concept as PyQueue:

* **FlaskQueue:** Flask-idiomatic version of the backend (minimal, explicit wiring)
* **DjangoQueue:** Django-idiomatic version (ORM patterns, project structure differences, admin tooling)

Goal: deepen understanding of how the **three primary Python web frameworks** solve the same backend problem with different philosophies.

### Additional near-term enhancements (PyQueuePro-immediate tasks)

* improved UI feedback (error toasts, better loading indicators)
* status-coloring and richer detail panels
* configurable worker count / queue parameters via env vars
* optional background persistence snapshots (simple DB or file store)

---

## Notes

This project is intentionally educational and comparative. Like SpringQueue (base) and GoQueue, the purpose is not just “make a queue,” but to build a practical intuition for:
* backend architecture boundaries
* concurrency models across ecosystems
* dependency injection patterns
* API contract discipline
* deployable full-stack shape with minimal UI
* comfort working in a Python/FastAPI (**most important, to be honest**)

---
