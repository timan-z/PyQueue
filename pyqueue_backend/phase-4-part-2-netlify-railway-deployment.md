# Deployment Notes – PyQueue (Railway + Netlify)

This document captures key lessons learned while deploying **PyQueue** across two platforms:

* **Backend**: Railway (FastAPI + Uvicorn)
* **Frontend**: Netlify (Vite + React + TypeScript)

The goal was a clean, production-style deployment where the backend is treated as the source of truth and the frontend adapts accordingly.

---

## Backend Deployment (Railway)

### 1. Python deployments require explicit dependency declaration

Unlike local development (where a virtual environment may already have packages installed), Railway requires an explicit dependency manifest.

**Key requirement:**

```text
requirements.txt
```

This file must include *all* runtime dependencies, for example:

```text
fastapi
uvicorn
python-dotenv
```

Without this file, Railway will successfully clone the repo but fail at runtime with errors such as:

```
ModuleNotFoundError: No module named 'fastapi'
```

**Lesson:**

> Python deployments do not implicitly infer dependencies — they must be declared.

---

### 2. Explicit start command is required

Railway does not automatically infer how to run a FastAPI application.

A custom start command must be provided:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Important details:

* `main:app` refers to `main.py` and the FastAPI instance named `app`
* `0.0.0.0` is required for containerized environments
* `$PORT` must be used (Railway injects this dynamically)

**Lesson:**

> Cloud platforms expect your service to bind to the platform-provided port.

---

### 3. Trailing slashes matter for CORS

CORS origin matching in FastAPI is **strict string comparison**.

A subtle but critical issue encountered:

* Railway automatically appends a trailing `/` to environment variables
* Browsers do *not* include a trailing slash in the `Origin` header

To prevent mismatches, the backend normalizes the origin:

```python
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "").rstrip("/")
```

This ensures:

* `https://pyqueue.netlify.app/` → `https://pyqueue.netlify.app`
* Already-correct values remain unchanged

**Lesson:**

> CORS operates on raw strings, not semantic URLs — normalization is essential.

---

### 4. Why `OPTIONS` returning 400 indicates a CORS misconfiguration

During debugging, the backend logs showed:

```
OPTIONS /api/enqueue 400 Bad Request
```

This is a strong diagnostic signal.

**Interpretation:**

* If CORS middleware matches the request, it intercepts `OPTIONS` and returns `200`
* A `400` means the request fell through to routing logic
* Therefore, the origin did not match the allowed origins

**Lesson:**

> An `OPTIONS 400` response almost always means the CORS middleware didn’t activate.

---

## Frontend Deployment (Netlify)

### 1. Vite environment variables must be prefixed

Netlify builds the frontend using Vite, which only exposes variables prefixed with `VITE_`.

Example:

```text
VITE_API_BASE=https://pyqueue-production.up.railway.app
```

Used in code as:

```ts
const API_BASE = import.meta.env.VITE_API_BASE.replace(/\/+$/, "");
```

The `.replace()` ensures consistency with backend URL handling.

---

### 2. Netlify build configuration

For this project, the Netlify configuration was:

* **Base directory**: project root
* **Build command**: `npm run build`
* **Publish directory**: `dist`
* **Functions directory**: *(not used)*

Once set, Netlify handled builds and static hosting without issue.

---

## Cross-Platform Takeaways

* The backend must be **explicit and defensive** (dependency lists, env normalization, startup commands)
* The frontend should **adapt to the backend contract**, not invent one
* Small inconsistencies (like trailing slashes) can cause large failures in distributed systems
* Logging environment variables early is an effective debugging technique
* Treating deployment as part of the engineering process (not an afterthought) surfaces real-world concerns early

---

## Final Reflection

Deploying PyQueue reinforced an important lesson:

> **Production readiness is less about adding features and more about eliminating ambiguity.**

By explicitly defining dependencies, normalizing inputs, and respecting platform conventions, PyQueue now runs cleanly across environments — and the same patterns will scale naturally into a future **PyQueuePro** deployment.
