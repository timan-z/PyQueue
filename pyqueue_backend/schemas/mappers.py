
from models.task import Task as DomainTask
from database.models import Task as OrmTask
from schemas.task import TaskResponse

def task_to_response(task: DomainTask) -> TaskResponse:
    return TaskResponse(
        id=task.t_id,
        payload=task.payload,
        type=task.t_type.value,
        status=task.status.value,
        attempts=task.attempts,
        max_retries=task.max_retries,
        created_at=task.created_at
    )

def orm_task_to_response(task: OrmTask) -> TaskResponse:
    return TaskResponse(
        id=task.task_id,
        payload=task.payload,
        type=task.task_type,
        status=task.status,
        attempts=task.attempts,
        max_retries=task.max_retries,
        created_at=task.created_at
    )
