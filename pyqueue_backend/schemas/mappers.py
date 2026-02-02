
from models.task import Task
from schemas.task import TaskResponse

def task_to_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.t_id,
        payload=task.payload,
        type=task.t_type.value,
        status=task.status.value,
        attempts=task.attempts,
        max_retries=task.max_retries,
        created_at=task.created_at.isoformat()
    )
