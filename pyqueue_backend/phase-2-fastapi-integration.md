# Phase 2 — FastAPI Integration & Pythonic Refactor

## Purpose of Phase 2

Phase 2 marks the transition of **PyQueue** from a direct, one-to-one translation of GoQueue and SpringQueue (base) into a **first-class FastAPI service** that follows Pythonic and framework-idiomatic practices. While Phase 1 focused on preserving behavioral parity across languages, Phase 2 intentionally prioritizes **API correctness, clarity, lifecycle management, and separation of concerns** as expected in real-world Python backend systems.

This phase establishes PyQueue as a production-shaped HTTP service rather than a standalone concurrency demo.

---

## FastAPI HTTP Integration

The core deliverable of Phase 2 was integrating PyQueue with FastAPI using idiomatic routing and request handling:

* REST endpoints were implemented using `APIRouter`, mirroring Spring’s `@RestController` pattern
* Request payloads were validated using **Pydantic models**
* Query parameters, path parameters, and error handling were expressed declaratively using FastAPI’s function signatures
* The HTTP API now cleanly exposes:

  * Task enqueueing
  * Job listing and filtering
  * Job inspection by ID
  * Retry semantics
  * Deletion and queue clearing

Unlike GoQueue (manual `http.HandleFunc`) or SpringQueue (annotation-driven magic), FastAPI’s explicit function signatures forced a clearer contract between **input validation, business logic, and output shape**, which directly influenced later refactors in this phase.

---

## Explicit Application Lifecycle (FastAPI Lifespan)

A key architectural shift in Phase 2 was embracing **FastAPI’s lifespan hooks** for startup and shutdown:

* The `Queue` runtime is created during application startup
* The executor is shut down cleanly during application shutdown
* No global threads or infinite loops are required to keep the process alive

This mirrors GoQueue’s explicit `main.go` bootstrapping model more closely than SpringQueue’s minimal `SpringQueueApplication.java`, which relies on Spring Boot’s implicit container lifecycle. In PyQueue, lifecycle management is explicit and visible, making system behavior easier to reason about and debug.

Notably, this also reflects modern FastAPI best practices, as legacy `@on_event` hooks are now deprecated in favor of lifespan context managers.

---

## Pythonic Refactors Introduced in Phase 2

Phase 2 introduced several deliberate Python-specific refactors that **do not exist** in GoQueue or SpringQueue (base), but are considered best practice in Python/FastAPI systems.

### 1. Dataclass-based Domain Model

The internal `Task` model was converted into a `@dataclass`, emphasizing:

* Clear data ownership
* Reduced boilerplate
* Explicit mutability for runtime state (status, attempts)

This keeps `Task` lightweight and focused on **runtime behavior**, not API concerns.

---

### 2. Centralized Task Creation via Factory Method

Task construction logic was normalized into a single factory method:

```python
Task.create(payload, t_type)
```

This ensures:

* Producers do not control ID generation or timestamps
* Retry logic is consistent and trivial
* Future migrations (DB persistence, tracing, UUIDs) are localized

This pattern did not exist in the base Go or Spring versions and was introduced specifically to support Pythonic evolution.

---

### 3. Internal Models vs Response Schemas

Phase 2 introduced a **hard separation** between:

* Internal runtime models (`models/task.py`)
* API response schemas (`schemas/task.py`)

Key motivations:

* Avoid leaking internal retry mechanics (`attempts`, `max_retries`)
* Prevent clients from coupling to internal implementation details
* Enable safe refactors without breaking API contracts
* Align with FastAPI’s OpenAPI-first philosophy

This separation was intentionally introduced **earlier** in PyQueue than in GoQueue or SpringQueue (base), where JSON serialization was mostly incidental. In FastAPI, schemas *are* the API, so this boundary is critical.

---

### 4. Explicit Mapping Layer

Rather than relying on implicit serialization (`from_attributes = True`), Phase 2 uses explicit mappers:

```python
task_to_response(task)
```

This makes transformations:

* Auditable
* Intentional
* Easy to extend (e.g., computed fields, redaction)

This design choice mirrors professional Python backends more closely than the earlier base projects.

---

## API-Facing Enums (Postman-Driven Insight)

A key Phase-2 realization emerged during Postman testing:

* Python `Enum(auto())` values serialize as integers
* API-facing enums must be **string-backed** for usability

As a result:

* `TaskType` and `TaskStatus` were converted to string enums
* FastAPI OpenAPI docs became cleaner
* Postman and frontend integration became intuitive

This is a FastAPI-specific concern that does not surface in GoQueue or SpringQueue (base), and it highlights how API tooling directly shapes backend design decisions.

---

## Safety Guards and Failure Modes

Phase 2 added a temporary safety guard (`require_queue`) to ensure routes fail gracefully if startup wiring breaks. This mirrors Spring’s “bean not available” behavior and prepares the codebase for a future dependency-injection refactor.

These guards will later map cleanly onto FastAPI’s `Depends()` system in Phase 3.

---

## Phase 2 Outcome

At the end of Phase 2, PyQueue is:

* A fully functional FastAPI service
* Explicitly bootstrapped with clean lifecycle management
* Backed by Pythonic domain models
* Protected by clear API boundaries
* Verified via Postman end-to-end testing
* Structurally ready for DI refactoring and frontend integration

Phase 3 will focus on:

* Code smell analysis
* Formal dependency injection
* CORS and frontend layering
* Final polish toward a portfolio-grade backend service
