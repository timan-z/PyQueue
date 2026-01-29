from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from enums.TaskStatus import TaskStatus
from task import Task

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

***
NOTE: Don't forget to save a snapshot of my post-GoQueue translation project state for future
documentation. I didn't do this with SpringQueuePro, and it's been a pain combing back through
old commits to write the architectural evolution document
"""
# DEBUG: Can add type hints for parameters but maybe leave the return type hints until after refactoring.
class Queue:
    # 0. Equivalent of SpringQueue's QueueService.java's constructor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.jobs: dict[str, Task] = {}  # This will be the task registry (equivalent of ConcurrentHashMap<String, Task> in SpringQueue).
        self.lock = Lock()  # Lock to protect shared state (there's no RWLock in Python. This and the {} above are queue.py's ConcurrentHashMap...)

    # 1. Translating - public void enqueue(Task t) {...}:
    def enqueue(self, task):
        task.status = TaskStatus.QUEUED
        if task.attempts == 0:
            task.max_retries = 3
        self.lock.acquire()
        try:
            self.jobs[task.t_id] = task
            self.executor.submit(task.execute)
        finally:
            self.lock.release()

    # 2. Translating - public void clear() {...}:
    def clear(self):
        self.lock.acquire()
        try:
            self.jobs.clear()
        finally:
            self.lock.release()

    # 3. Translating - public Task[] getJobs() {...}:
    def get_jobs(self):
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

    # 4. Translating - public Task getJobById(String id) {...}:
    def get_job_by_id(self, t_id: str):
        self.lock.acquire()
        t = None
        try:
            if t_id in self.jobs:
                t = self.jobs[t_id]
        finally:
            self.lock.release()
        return t

    # 5. Translating - public boolean deleteJob(String id) {...}:
    def delete_job(self, t_id: str):
        self.lock.acquire()
        res = False
        try:
            if t_id in self.jobs:
                del self.jobs[t_id]
                res = True
        finally:
            self.lock.release()
        return res

    # Helper methods:
    def get_job_count(self):
        return len(self.jobs)

    # Shutdown method:
    def shutdown(self):
        print("Seems like this should just be a stub for now?")
