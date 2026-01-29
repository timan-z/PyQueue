import datetime
from enums.TaskStatus import TaskStatus
from enums.TaskType import TaskType

class Task:
    def __init__(self, t_id: str, payload: str, t_type: TaskType, status: TaskStatus, attempts: int, max_retries: int, created_at: datetime.datetime):
        self.t_id = t_id
        self.payload = payload
        self.t_type = t_type
        self.status = status
        self.attempts = attempts
        self.max_retries = max_retries
        self.created_at = created_at
