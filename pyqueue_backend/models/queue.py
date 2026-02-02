from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Optional, Callable

from models.task import Task

# 2026-02-01-NOTE: Adding this to fix circular dependency that I masked earlier w/ a local import in enqueue():
WorkerFactory = Callable[[Task, "Queue"], Callable[[], None]]
"""
^ WorkerFactory is just a function that knows how to create something that can execute a task.
The arguments within Callable is the input [Task, "Queue"] ("Queue" is forward ref) and output Callable[[], None].
(NOTE: The output being Callable[[], none] means the return type is another function that takes no arguments and returns nothing).
This maps well to ThreadPoolExecutor because self.executor.submit(runnable) expects runnable: Callable[[], Any]. 
"""

"""
Avoid using async def, FastAPI background tasks, asyncio.Queue, and so on for now.
- Like my progression w/ SpringQueue (base), I want to first directly translate GoQueue, then idiomatically refactor.
- Going to use ThreadPoolExecutor for this first stage (ExecutorService-equivalent) before taking advantage of FastAPI.

NOTE: My queue.py will certainly resemble SpringQueue's QueueService.java more so than it would queue.go
because Python, for these purposes, aligns more closely with Java than Go in how concurrency is expressed.

```(slap this paragraph below into the README later):
Go encourages developers to model concurrency explicitly using goroutines and channels as first-class language
primitives, whereas Python—like Java—expects concurrency to be delegated to the runtime via executors and 
thread pools. Rather than manually scheduling work or managing worker fan-out, Python code typically submits 
callables to an executor and lets the runtime handle scheduling, lifecycle, and resource management. As a 
result, this Queue acts as a coordinating service (similar to Java’s ExecutorService) rather than a low-level 
concurrency primitive, which better reflects idiomatic and production-realistic Python backend design.
```
- Like SpringQueue, my Python Queue is not a data structure but a service object for tracking tasks, submitting work, and managing lifecycle.
- Since I'm following SpringQueue as a map more than GoQueue, and jumping straight to using ThreadPoolExecutor,
I'm saving some time and don't need GoQueue-specific methods like dequeue() since it's automated here.

- THE BIG ERGONOMIC CHANGE:
```
In the original SpringQueue implementation, Worker implements Java’s Runnable interface, allowing an ExecutorService 
to accept a Worker object and implicitly invoke its run() method (executor.submit(new Worker(task, queue))). 
Python’s ThreadPoolExecutor does not support this object-centric execution model; instead, it executes explicit 
callables (functions or bound methods) with no implicit interface lookup. During the initial translation, this mismatch 
surfaced when attempting to submit task.execute and defining Worker.run(task)—both of which conflict with Python’s 
execution semantics. The correct Python mapping is to treat Worker as a stateful execution unit that owns its Task, 
expose a zero-argument run() method, and submit the bound method (worker.run) directly to the executor. 
This preserves SpringQueue’s separation of data (Task) and behavior (Worker) while adapting cleanly to Python’s more 
explicit, function-driven concurrency model.
```

***
NOTE: Don't forget to save a snapshot of my post-GoQueue translation project state for future
documentation. I didn't do this with SpringQueuePro, and it's been a pain combing back through
old commits to write the architectural evolution document
"""
# DEBUG: Can add type hints for parameters but maybe leave the return type hints until after refactoring.
class Queue:
    """
    This is the runtime coordination service for Tasks. (Equivalent of queue.go and QueueService.java).
    It owns:
    - Task Registry
    - Worker execution lifecycle
    - Thread pool
    """

    # 0. CONSTRUCTOR - Equivalent of SpringQueue's QueueService.java's constructor:
    def __init__(self, worker_factory: WorkerFactory) -> None:
        self.executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)   # TO-DO:+DEBUG: Eventually change max_workers to be configurable (like I did in SpringQueuePro -- later).
        self.jobs: dict[str, Task] = {}  # This will be the task registry (equivalent of ConcurrentHashMap<String, Task> in SpringQueue).
        self.lock: Lock = Lock()  # Lock to protect shared state (there's no RWLock in Python. This and the {} above are queue.py's ConcurrentHashMap...)
        self.worker_factory = worker_factory

    # 1. Enqueue a task: Translating - public void enqueue(Task t) {...}:
    def enqueue(self, task: Task) -> None:
        """
        Registers a Task and submits it for execution.
        Assumes the task is already fully initialized.
        """
        #from system.worker import Worker    # TO-DO: This will be lifted out of here when FastAPI Dependency Injection is layered in.

        # 2026-01-31: Original Lock and release effect replaced with context manager - lock lifts when all lines are executed (basically just shortens code):
        with self.lock:
            self.jobs[task.t_id] = task

        runnable = self.worker_factory(task, self)
        self.executor.submit(runnable)
        # Earlier stage legacy code (code structure directly from the SpringQueue and GoQueue translation phase):
        """
        task.status = TaskStatus.QUEUED
        if task.attempts == 0:
            task.max_retries = 3
        self.lock.acquire()
        try:
            self.jobs[task.t_id] = task
            worker = Worker(task, self)
            self.executor.submit(worker.run)
        finally:
            self.lock.release()
        """

    # 2. Clear all jobs: Translating - public void clear() {...}:
    def clear(self) -> None:
        with self.lock:
            self.jobs.clear()

    # 3. Get all jobs (snapshot): Translating - public Task[] getJobs() {...}:
    def get_jobs(self) -> list[Task]:
        # Returns a snapshot of all tracked tasks:
        with self.lock:
            return list(self.jobs.values())
        # Earlier stage legacy code:
        """
        self.lock.acquire()
        #all_tasks: list[Task] | list[None] = [None] * len(self.jobs)
        all_tasks = []
        try:
            #i = 0
            for key, val in self.jobs.items():
                #all_tasks[i] = val
                all_tasks.append(val)
                #i += 1
        finally:
            self.lock.release()
        return all_tasks
        """

    # 4. Get job by ID: Translating - public Task getJobById(String id) {...}:
    def get_job_by_id(self, t_id: str) -> Optional[Task]:
        with self.lock:
            return self.jobs.get(t_id)

    # 5. Delete job: Translating - public boolean deleteJob(String id) {...}:
    def delete_job(self, t_id: str) -> bool:
        with self.lock:
            if t_id in self.jobs:
                del self.jobs[t_id]
                return True
            return False

    # Helper methods:
    def get_job_count(self) -> int:
        with self.lock:
            return len(self.jobs)

    # Shutdown method:
    def shutdown(self) -> None:
        #print("Seems like this should just be a stub for now?")
        self.executor.shutdown(wait = True)
