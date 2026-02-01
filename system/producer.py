from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
# Custom imports:
from models.queue import Queue
from enums.TaskType import TaskType
from enums.TaskStatus import TaskStatus
from models.task import Task

from schemas.mappers import task_to_response
from schemas.task import TaskResponse

"""
This producer.py file would certainly be more closely modeled after ProducerController.java than producer.go.
"""

router = APIRouter(prefix="/api") # Equivalent of @RequestMapping("/api") - APIRouter is essentially @RestController

# FastAPI's model doesn't use constructors here so I need to do module-level injection for things like Queue (not yet going to touch its DI):
queue: Queue | None = None

def set_queue(q: Queue):
    global queue
    queue = q

# Equivalent of ProducerController.java's "public static class EnqueueRequest { public String payload; public String type }":
class EnqueueRequest(BaseModel):
    payload: str
    t_type: TaskType

# 0. Translating routes. NOTE: In my ProducerController.java, the methods were all "handle_enqueue" and named like that (because I was translating directly from Go and copied its wording conventions).

# 2026-01-31: Temp helper for checking if the Queue is initialized (will be removed in the final pass of this Phase where I introduce FastAPI DI w/ depends):
def require_queue() -> Queue:
    if queue is None:
        raise HTTPException(status_code=503, detail="Queue not initialized (service unavailable)")
    return queue

# 1. Translating - @PostMapping("/enqueue") ... public ResponseEntity<Map<String, String>> handleEnqueue(@RequestBody EnqueueRequest req) {...}:
@router.post("/enqueue", response_model=dict[str,str])
def enqueue(req: EnqueueRequest) -> dict[str, str]:
    q = require_queue()
    #created_at = datetime.datetime.now() #.strftime("%Y-%m-%d %H:%M:%S")  # Translating what I did w/ LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    task = Task.create(req.payload, req.t_type)
    q.enqueue(task)
    return { "message": f"Job {task.t_id} (Payload: {task.payload}, Type: {task.t_type}) enqueued!" }

# 2. Translating - @GetMapping("/jobs") ... public ResponseEntity<List<Task>> handleListJobs(@RequestParam(required = false) String status) {...}:
"""
NOTE(S)-TO-SELF:
- Query parameters in FastAPI are just function parameters, and for optional params you'd just do Optional[T] (or T | None) and then Query(...)
- [@RequestParam(required = false) String status] becomes [status: Optional[str] = Query(default = None)]
"""
@router.get("/jobs", response_model=list[TaskResponse])
def get_jobs(status: Optional[str] = Query(default = None)) -> list[TaskResponse]:
    q = require_queue()
    all_jobs = q.get_jobs()
    status_enum: Optional[TaskStatus] = None
    if status is not None:
        try:
            status_enum = TaskStatus[status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid status filter")

    return [
        task_to_response(t)
        for t in all_jobs
        if status_enum is None or t.status == status_enum
    ]
    # Old code (refactored to the more verbose but safer version above because the list calculations inside do some dangerous tight coupling):
    """
    all_jobs = q.get_jobs()
    filtered = [ task_to_response(t) for t in all_jobs if status is None or t.status.name.lower() == status.lower() ]
    return filtered
    """

# 3. Translating @GetMapping("/jobs/{id}") ... public ResponseEntity<Task> handleGetJobById(@PathVariable String id) {...}
@router.get("/jobs/{job_id}", response_model=TaskResponse)
def get_job(job_id: str) -> TaskResponse:
    q = require_queue()
    task = q.get_job_by_id(job_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return task_to_response(task)

# 4. Translating @PostMapping("/jobs/{id}/retry") ... public ResponseEntity<?> handleRetryJobById(@PathVariable String id) {...}
@router.post("/jobs/{job_id}/retry", response_model=TaskResponse)
def retry_job(job_id: str) -> TaskResponse:
    q = require_queue()
    task = q.get_job_by_id(job_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found. Could not be retried.")
    if task.status != TaskStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Job {job_id} is not a failed Task. Can only retry failed Tasks.")
    task_clone = Task.create(task.payload, task.t_type)
    q.enqueue(task_clone)
    return task_to_response(task_clone)

# 5. Translating @DeleteMapping("/jobs/{id}") ... public ResponseEntity<?> handleDeleteJobById(@PathVariable String id) {...}
@router.delete("/jobs/{job_id}", response_model=dict[str,str])
def delete_job(job_id: str) -> dict[str, str]:
    q = require_queue()
    result = q.delete_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found. Could not be deleted.")
    return { "message": f"Job {job_id} deleted!" }

# 6. @PostMapping("/clear") ... public ResponseEntity<?> clearQueue() {...}
@router.post("/clear", response_model=dict[str,str])
def clear_queue() -> dict[str, str]:
    q = require_queue()
    q.clear()
    return { "message": "All jobs in the queue cleared!" }
