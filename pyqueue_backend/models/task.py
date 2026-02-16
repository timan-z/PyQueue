"""
DEPRECATED:
In-memory Task model.
Replaced by database.models.Task (SQLAlchemy ORM).
Kept temporarily during migration phase.
"""
import datetime
import time
from dataclasses import dataclass
from enums.TaskStatus import TaskStatus
from enums.TaskType import TaskType

@dataclass
class Task:
    t_id: str
    payload: str
    t_type: TaskType
    status: TaskStatus
    attempts: int
    max_retries: int
    created_at: datetime.datetime

    """
    2026-01-31-NOTE:
    "create" method below is the new single source for ID generation, timestamps, and setting retry defaults.
    Better because:
    - Producers no longer know how tasks are initialized.
    - Retry logic becomes trivial and consistent.
    - Easier for later migrations (DB persistence, tracing IDs, etc).
    ALSO:
    The -> "Task" you see is a forward reference. (Python evaluates type annotations at function definition time
    so Task won't yet exist as a fully bound name -- that's why you need to do "Task", that's the workaround basically).
    """
    @classmethod
    def create(cls, payload: str, t_type: TaskType) -> "Task":
        return cls(
            t_id=f"Task-{time.perf_counter_ns()}",
            payload=payload,
            t_type=t_type,
            status=TaskStatus.QUEUED,
            attempts=0,
            max_retries=3,
            created_at=datetime.datetime.now(),
        )

# Phase 1-2 (pre-@dataclass introduction) legacy code:
"""
class Task:
    # Had a realization that when I instantiate new Tasks in SpringQueue, SpringQueuePro, and GoQueue
    # I'm only actually providing the payload and TaskType (everything else is provided and determined by the system).
    # The (original) __init__ constructor I have below is more of a storage model than a creation model:
    # EDIT: ^ nvm I don't know what I'm talking about -- but maybe I should adjust this a bit to delegate multiple
    # constructors to @classmethod (Python only allows for one constructor normally but there are workarounds).
    
    def __init__(self, t_id: str, payload: str, t_type: TaskType, status: TaskStatus, attempts: int, max_retries: int, created_at: datetime.datetime):
        self.t_id = t_id
        self.payload = payload
        self.t_type = t_type
        self.status = status
        self.attempts = attempts
        self.max_retries = max_retries
        self.created_at = created_at
"""