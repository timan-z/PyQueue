import datetime
from enums.TaskStatus import TaskStatus
from enums.TaskType import TaskType

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
