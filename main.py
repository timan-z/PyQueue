import time

from fastapi import FastAPI

import datetime
from models.queue import Queue
from models.task import Task
from enums.TaskType import TaskType
from enums.TaskStatus import TaskStatus

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

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

def main():
    # Some test code before setting up HTTP routes and that stuff...
    q = Queue()
    # Some test Tasks:
    t1 = Task("Task 1", "Payload 1", TaskType.EMAIL, TaskStatus.QUEUED, 0, 3, datetime.datetime.now())
    # NOTE: Maybe I should adjust task.py so that status isn't set or is just set to None?
    t2 = Task("Task 2", "Payload 2", TaskType.NEWSLETTER, TaskStatus.QUEUED, 0, 3, datetime.datetime.now())
    t3 = Task("Task 3", "Payload 3", TaskType.DATACLEANUP, TaskStatus.QUEUED, 0, 3, datetime.datetime.now())
    # Test enqueue:
    q.enqueue(t1)
    q.enqueue(t2)
    q.enqueue(t3)

    while True:
        time.sleep(2)

if __name__ == "__main__":
    main()
