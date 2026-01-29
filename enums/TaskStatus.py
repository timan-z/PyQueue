from enum import Enum, auto

class TaskStatus(Enum):
    QUEUED = auto()
    INPROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
