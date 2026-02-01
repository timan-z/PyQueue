from enum import Enum

# See "2026-01-31" stamped comment I left at the top of enums/TaskType.py
class TaskStatus(Enum):
    QUEUED = "QUEUED"
    INPROGRESS = "INPROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
