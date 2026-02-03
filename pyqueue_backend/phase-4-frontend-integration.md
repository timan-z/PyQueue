# PyQueue — Phase 4: Frontend Integration (React + TypeScript + Vite)

> **Phase goal:** Reuse the minimal GoQueue / SpringQueue (base) React-TS dashboard, but adapt it to PyQueue’s stricter, more explicit FastAPI contract (schemas, enums, DI-driven service wiring).  
> **Key theme:** **Backend is the source of truth** — the frontend “bends” to match PyQueue’s request/response shapes and vocabulary.

---

## 0) Context: What Phase 4 is (and is not)

### What Phase 4 *is*
- Integrating the existing “Queue Dashboard” frontend (Vite + React + TS) against the **PyQueue backend API**.
- Hardening the API boundary so the frontend consumes **exact DTOs** returned by FastAPI.
- Cleaning up mismatches that were “loose” in earlier projects (raw strings, camelCase, implied semantics).

### What Phase 4 *is not*
- A UI redesign or a PyQueuePro frontend build.
- Deep UX improvements, filtering systems, or advanced visualizations.
- Persistence, observability, multi-tenant rooms, auth, etc. (those belong to later phases / PyQueuePro).

---

## 1) Monorepo structure and project layout

PyQueue was reorganized into a monorepo to cleanly separate concerns:

```
/PyQueue-Backend
- /enums
- /models
- /schemas
- /system
- main.py
/PyQueue-Frontend
- /src
- /components
-- JobDisplay.tsx
-- JobsList.tsx
-- LoadingSpinner.tsx
- /utility
-- api.ts
-- types.ts
- App.tsx
- App.css
- main.tsx
````
**Reasoning:** This separation clarifies that:
- Backend owns the *contract* and runtime logic.
- Frontend is an *external client* consuming that contract.
- Each side can be hosted independently (Railway backend, Netlify frontend) with environment-driven configuration.

---

## 2) PyQueue backend contract that drove all frontend changes

Earlier projects (GoQueue / SpringQueue base) were more permissive:
- task types were passed as raw strings
- response shapes often matched UI preferences
- enum vocabulary and casing were sometimes implicit

PyQueue is more explicit:
- **FastAPI schemas define the public contract** (`TaskResponse`)
- internal model fields differ from external API fields
- enum values are canonical, stable strings

### Core API endpoints used by the frontend
- `POST /api/enqueue`
- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `POST /api/jobs/{job_id}/retry`
- `DELETE /api/jobs/{job_id}`
- `POST /api/clear`

---

## 3) The two main mismatches (and how they were resolved)

### Mismatch A: Field names and wire format (snake_case vs camelCase)
In PyQueue, the API contract is backend-defined and FastAPI-native, so responses favor **snake_case** and explicit serialization choices (ISO timestamps).

**Example:**
- Frontend (old): `createdAt`
- Backend (PyQueue): `created_at` (ISO-8601 string)

The fix: **Frontend types and component reads were updated to match the exact backend DTO.**

---

### Mismatch B: Enum vocabulary and casing
PyQueue uses enums for `TaskType` and `TaskStatus`. The backend emits canonical enum values:

- Status values: `"QUEUED"`, `"INPROGRESS"`, `"COMPLETED"`, `"FAILED"`
- Type values: `"EMAIL"`, `"REPORT"`, `"DATACLEANUP"`, `"SMS"`, `"NEWSLETTER"`, `"TAKESLONG"`, `"FAIL"`, `"FAILABS"`, `"TEST"`

Earlier projects used UI-friendly strings (e.g., `"fail-absolute"`, `"data-cleanup"`, `"failed"`), which diverged from PyQueue’s contract.

The fix: **Introduce a translation layer in `api.ts`** that maps UI values to backend enum values, while keeping backend vocabulary strict.

---

## 4) Frontend code changes (what changed and why)

### 4.1 `src/utility/types.ts` — redefined Task as the backend DTO

#### Why this file mattered
In GoQueue and SpringQueue base, the frontend’s `Task` shape included UI-driven fields and casing conventions. PyQueue formalized the contract, so the frontend had to stop “inventing” types and instead reflect the wire format.

#### Final PyQueue-aligned `Task`
```ts
export interface Task {
  id: string;
  payload: string;
  type: string;        // backend enum value (e.g. "EMAIL")
  status: string;      // backend enum value (e.g. "FAILED")
  attempts: number;
  max_retries: number;
  created_at: string;  // ISO-8601 timestamp (PyQueue-specific)
}
````

#### Why `interface` instead of `type`

Both work in TypeScript, but `interface` communicates:

* “this is a stable DTO / contract shape”
* easier future extension via `extends` (e.g., `TaskView extends Task { ... }`)

This matches the intent of a backend-defined schema.

---

### 4.2 `src/utility/api.ts` — turned into a true boundary adapter

#### The role of `api.ts` in Phase 4

`api.ts` became the formal boundary adapter between UI and backend, responsible for:

* translating UI-friendly inputs into backend-valid request payloads
* preserving backend responses verbatim (no implicit reshaping)
* ensuring the backend remains the source of truth

#### Key change: mapping UI task type → backend enum

The UI still uses dropdown values like `"fail-absolute"` for human readability. PyQueue expects `"FAILABS"`. The mapping resolves that discrepancy without weakening backend strictness.

```ts
const TASK_TYPE_MAP: Record<string, string> = {
  "email": "EMAIL",
  "report": "REPORT",
  "data-cleanup": "DATACLEANUP",
  "sms": "SMS",
  "newsletter": "NEWSLETTER",
  "takes-long": "TAKESLONG",
  "fail": "FAIL",
  "fail-absolute": "FAILABS",
};
```

Enqueue now uses:

```ts
body: JSON.stringify({
  payload,
  t_type: backendType, // backend enum value
})
```

**Important:** `t_type` is the backend request key, matching `EnqueueRequest` in FastAPI.

---

## 5) Component changes

Phase 4’s component-level work largely fell into two buckets:

### 1. Fix status checks to match backend enum vocabulary

Earlier frontends checked status like:

* `"failed"` (lowercase)

PyQueue emits:

* `"FAILED"` (uppercase enum value)

So checks must become:

```tsx
job?.status === "FAILED"
```

This is crucial because:

* it preserves backend ownership of meaning
* avoids accidental “semantic drift” across clients

---

### 2. Timestamp display: render-time formatting only

PyQueue returns:

* `created_at` as ISO-8601 string

The frontend should:

* keep `created_at` untouched in `types.ts`
* format only at render time (presentation layer)

Example (used in JobDisplay):

```tsx
<div>
  <b>Created At:</b>{" "}
  {job ? new Date(job.created_at).toLocaleString() : ""}
</div>
```

**Why this matters:** It keeps the API boundary clean, and the UI flexible.

---

### 5.1 `JobDisplay.tsx` updates (most important)

This component had the highest mismatch risk because it reads many fields and contained status-driven behavior (Retry button).

Key updates:

* updated field reads:

  * `maxRetries` → `max_retries`
  * `createdAt` → `created_at` (formatted)
* updated Retry visibility:

  * `"failed"` → `"FAILED"`

It also aligned to the updated API contract that exposes:

* `attempts`
* `max_retries`

---

### 5.2 `JobsList.tsx` (minimal impact)

`JobsList` mostly displays:

* `id`
* `status`

Because it doesn’t interpret status semantics or format timestamps, it required little/no changes beyond type alignment.

---

### 5.3 `App.tsx` (minimal impact)

`App.tsx` primarily:

* orchestrates state and event handlers
* calls `api.ts`
* passes selected jobs into children

Most meaningful changes were copy / branding (later polish), not core integration.

---

## 6) Backend detour: exposing runtime metadata for introspection

During Phase 4, a prior deviation to not expose attempts and max_retries externally was "walked back" (now they *are* exposed in API responses, etc):

* `attempts`
* `max_retries`

### Why

Even though this minimal dashboard is intentionally simple, PyQueue is meant to lead toward PyQueuePro, where the UI is explicitly introspection-focused (similar to SpringQueuePro’s “inspect task details”).

So these were updated:

* `TaskResponse` to include these fields
* `task_to_response` mapper to serialize them
* frontend `Task` interface to match

This preserved the backend-first rule:

* frontend does not invent attempts/max retries
* backend explicitly chooses to expose them in the contract

---

## 7) Deployment readiness: env vars + CORS

Because Phase 4 is specifically about integration and hosting readiness, environment-driven configuration on both sides were configured.

### Frontend (Netlify / Vite)

In `api.ts`:

```ts
const API_BASE = import.meta.env.VITE_API_BASE.replace(/\/+$/, "");
```

Local `.env` example:

```
VITE_API_BASE=http://127.0.0.1:8000
```

Netlify will set `VITE_API_BASE` to the Railway backend URL.

---

### Backend (Railway / FastAPI)

FastAPI does not automatically read `.env`, so the backend must explicitly load env vars in local development, and Railway will inject them in production.

Key usage: controlling `allow_origins` for CORS via env var(s).

Typical pattern:

* define `FRONTEND_ORIGIN` (or `FRONTEND_ORIGINS`)
* use it to set `allow_origins=[...]`

**Principle:** Backend owns who may call it — the frontend does not “decide” CORS.

---

## 8) Minor styling polish (CSS)

Styling in Phase 4 was intentionally minor compared to the core work, but was present to signify a degree of separation from GoQueue and SpringQueue (base edition). Here is what it encompassed):
* move toward a FastAPI/teal accent (`#009688`)
* lighten the palette to be more vibrant (less “dark dashboard”)
* optionally introduce CSS variables for a small color system:

  * background
  * accent
  * hover
  * shadow
---

## 9) Final Phase 4 outcome

At the end of Phase 4, PyQueue has:

- A working Vite + React + TypeScript dashboard
- Strict contract alignment with the FastAPI backend
- Enum vocabulary mismatch resolved cleanly in the boundary layer (`api.ts`)
- DTO correctness enforced via `types.ts`
- Status handling and timestamp formatting fixed (B3/B4)
- Environment-variable driven configuration for deployment
- A coherent “backend-first” integration story consistent with SpringQueuePro practices

---

## 10) Lessons learned (Phase 4 takeaways)

1. **DTOs are contracts, not conveniences**

   * PyQueue’s schemas forced a clean split between internal models and API shape.

2. **A boundary adapter is non-negotiable**

   * `api.ts` is where UI-friendly inputs become backend-valid requests.

3. **Enums demand vocabulary discipline**

   * A backend emitting `"FAILED"` means the frontend must not assume `"failed"`.

4. **Timestamps are a wire format problem + a UI formatting problem**

   * Keep ISO strings in the contract; format only at render time.

5. **Deployment forces correctness**

   * env vars + CORS become first-class concerns once frontend and backend are hosted separately.

---
