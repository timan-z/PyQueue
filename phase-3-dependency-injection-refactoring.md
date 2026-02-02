# Phase 3 — Code Smell Refactor & Dependency Injection

## Purpose of Phase 3

Phase 3 represents the final structural refactor of **PyQueue (base)** before frontend integration and CORS configuration. The goal of this phase was **not feature expansion**, but **architectural cleanup**: identifying and removing code smells introduced during early translation, aligning the project with idiomatic FastAPI patterns, and preparing the system for long-term maintainability.

Concretely, Phase 3 focused on:

* Eliminating hidden dependencies and circular imports
* Introducing explicit, framework-native dependency injection
* Clarifying ownership boundaries between HTTP, runtime, and execution layers
* Reducing implicit global state and startup ordering assumptions

This phase mirrors the kind of refactoring pass commonly performed after an initial prototype stabilizes and before a system is extended further.

---

## Code Smell Scan & Structural Improvements

### 1. Removing Global Mutable State

**Problem (Pre-Phase 3):**
Early versions of PyQueue relied on:

* A module-level `queue` variable
* `set_queue(...)` during startup
* Guard helpers like `require_queue()`

While functional, this approach:

* Coupled `producer.py` tightly to startup order
* Made unit testing more difficult
* Bypassed FastAPI’s built-in dependency system
* Introduced implicit global state

**Resolution:**
Queue ownership was moved into FastAPI’s lifecycle and application state:

* `Queue` is instantiated in `main.py` during startup
* Stored in `app.state.queue`
* Accessed exclusively via FastAPI dependency injection

This removes globals entirely and aligns PyQueue with production FastAPI architecture.

---

### 2. Introducing FastAPI Dependency Injection

FastAPI’s dependency injection system was layered in using `Depends(...)`.

```python
def get_queue(request: Request) -> Queue:
    return request.app.state.queue
```

All producer routes now explicitly declare their dependency:

```python
@router.post("/enqueue")
def enqueue(
    req: EnqueueRequest,
    q: Queue = Depends(get_queue),
):
    ...
```

**Benefits:**

* Dependencies are explicit and discoverable
* No reliance on shared mutable module state
* Routes are trivially testable with mocked dependencies
* Mirrors Spring’s `@Autowired` / application context model
* Matches idiomatic FastAPI expectations

At this point, PyQueue’s HTTP layer is **fully DI-driven**.

---

### 3. Clarifying Layer Boundaries

By the end of Phase 3, PyQueue cleanly separates concerns:

```
HTTP layer        → producer.py (FastAPI routes + Depends)
Domain runtime    → queue.py / worker.py
Domain model      → Task (dataclass)
API contract      → TaskResponse (Pydantic)
Lifecycle         → main.py (lifespan + app.state)
```

This separation ensures:

* Execution logic does not leak into API code
* API response shape is decoupled from runtime internals
* Lifecycle concerns remain centralized and explicit

---

### 4. Addressing the Worker Import Smell

**Problem:**
`Queue.enqueue()` imported `Worker` internally:

```python
from system.worker import Worker
```

This was a **known smell**:

* Queue knew too much about execution details
* Created tighter coupling than necessary
* Risked circular dependencies as the system grows

**Resolution (Phase 3 Decision):**
Rather than deferring, this dependency was intentionally **acknowledged and documented** as the final acceptable coupling in PyQueue (base).

Why this is acceptable *for now*:

* Worker creation is a runtime concern, not HTTP
* Queue remains the coordination service (matching SpringQueue’s role)
* DI has already eliminated the most dangerous global coupling

This sets a **clear boundary** for PyQueuePro:

> Future iterations will introduce a worker factory or execution strategy abstraction, fully decoupling Queue from Worker instantiation.

---

### 5. Safer Enum Handling & API Validation

During Phase 3, enum usage was finalized for API safety:

* `TaskType` and `TaskStatus` are string-backed enums
* Incoming query parameters are explicitly validated and converted
* Invalid enum values now return clean `400` responses

This avoids brittle string comparisons and ensures API behavior remains stable as task types evolve.

---

## Outcome of Phase 3

By the end of Phase 3:

* PyQueue no longer relies on globals
* All runtime services are DI-managed
* Startup/shutdown is lifecycle-safe
* Execution and API layers are cleanly separated
* Known architectural limitations are documented and intentional

At this point, **PyQueue (base) is architecturally complete**.

Any further evolution (persistence, execution strategies, metrics, frontend, CORS, etc.) naturally belongs in **PyQueuePro**, rather than complicating the base system.

---

## Summary

Phase 3 demonstrates the transition from a working prototype to a production-ready backend service. By removing global state, introducing FastAPI’s dependency injection, and clarifying architectural boundaries, PyQueue now reflects real-world backend design practices rather than framework-agnostic translation code. This mirrors the same evolution I applied in later iterations of my Spring-based systems, but adapted to Python and FastAPI idioms.
