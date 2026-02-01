from fastapi import FastAPI
from models.queue import Queue
from system.producer import router
from contextlib import asynccontextmanager

"""
For later documentation - some notes on layering in FastAPI's Dependency Injection:
```
Before layering in FastAPI's Dependency Injection, my main.py declares Queue as a global mutable state. 
This is harder to test and tightly couples producer.py to startup ordering (it's not how FastAPI idiomatically expects services to be shared).

To layer in FastAPI's DI, I need to store Queue on app.state and then access it with Depends(...)
- I shouldn't be using globals, set_queue, or require_queue
(And this mirrors Spring's application context, request-scoped DI, and of course production FastAPI patterns).

app.state is FastAPI's official shared application container (and in it we declare one queue instance for the entire app).
```
"""

@asynccontextmanager
async def lifespan(the_app: FastAPI):
    # 2026-02-01-NOTE: FastAPI DI Refactor.
    # On startup:
    the_app.state.queue = Queue()
    try:
        yield
    finally:
        # shutdown
        the_app.state.queue.shutdown()

    # [EDIT: Pre-DI Legacy Code] on startup:
    """
    q = Queue()
    set_queue(q)

    try:
        yield
    finally:
        # on shutdown:
        q.shutdown()
    """

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# PyCharm's default FastAPI set-up code:
"""
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
"""

"""
During the SpringQueue-Translation phase, main.py will be responsible for:
- Instantiating the Queue defined in queue.py
- Potentially enqueueing a few test tasks
- Keep the process alive long enough to observe workers
- Handle shutdown cleanly
AFTER translation AND refactoring, it'll be time to layer in and take advantage of FastAPI.
***
ALSO:
- This main.py is the rare instance where I would be referring to GoQueue's main.go more than I would SpringQueue's SpringQueueApplication.java file.
- SpringQueueApplication.java is bare because Spring automates lifecycle and wiring (component scan, DI, auto-start), it's all implicit.
- In GoQueue's main.go, the lifecycle and wiring is explicit (and it would be the same in PyQueue too, at this stage).

For later documentation:
```
In SpringQueue, SpringQueueApplication.java is intentionally minimal because Spring Boot handles nearly all lifecycle and 
wiring concerns automatically through component scanning, dependency injection, and managed startup/shutdown hooks. 
By contrast, Python in this Phase-1 PyQueue translation behaves much more like GoQueue: there is no framework-level container 
automatically instantiating services and injecting dependencies, so main.py must explicitly bootstrap the runtime by creating 
the Queue instance, submitting work to the executor, keeping the process alive long enough for background workers to run, 
and shutting down cleanly. In other words, even though PyQueue lives inside a FastAPI project, the translation phase requires 
a Go-style “explicit wiring” entrypoint rather than Spring’s “implicit wiring” application launcher.
```
"""
