import os
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.queue import Queue
from system.producer import router
from routes.db_tasks import router as db_router
from system.worker import Worker
from contextlib import asynccontextmanager
from database.base import Base
from database.engine import engine
from sqlalchemy.exc import OperationalError

# 2026-02-18: SOME ARBITRARY COMMENT TO CAUSE A MERGE CONFLICT!!!

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

load_dotenv()
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").rstrip("/")

if not FRONTEND_ORIGIN:
    raise RuntimeError("FRONTEND_ORIGIN is not set")

print("FRONTEND_ORIGIN =", os.getenv("FRONTEND_ORIGIN"))

def worker_factory(task, queue):
    return Worker(task, queue).run

Base.metadata.create_all(bind=engine)   # Creating the schema for tables if it's not there in the Docker MySQL instance or local instance.
# Config for structure logs I'll be adding:
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
# Initializing Sentry for FastAPI:
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("APP_ENV", "development"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)

print("DEBUG: print check")
#print("DEBUG: SENTRY_DSN = ", os.getenv("SENTRY_DSN"))

@asynccontextmanager
async def lifespan(the_app: FastAPI):
    # 2026-02-01-NOTE: FastAPI DI Refactor.
    # On startup:
    the_app.state.queue = Queue(worker_factory=worker_factory)
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
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
# ^ TO-DO: ^ I should 100% externalize the origins destination to an environmental variable (need this for Railway deployment later anyways).
app.include_router(router)
app.include_router(db_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# SENTRY-LEARNING: Unhandled exception - Sentry catches automatically and sends to the server/sentry.io site.
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

# SENTRY-LEARNING: These are handled exceptions that I'm supposed to manually mark sentry to "capture" and send up to the server.
@app.get("/infra-error")
async def infra_error():
    try:
        raise OperationalError("DataBase down", None, None)
    except OperationalError as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# SENTRY-LEARNING: Playing around with and getting a feel for breadcrumbs.
@app.get("/breadcrumb-demo")
async def breadcrumb_demo():
    sentry_sdk.add_breadcrumb(
        category="task",
        message="User attempted risky operation",
        level="info",
    )
    return 1 / 0

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
