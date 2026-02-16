import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from services.task_service import TaskService
from database.models import Task as OrmTask
from schemas.task import TaskResponse
from schemas.task import TaskCreate
from schemas.mappers import orm_task_to_response

router = APIRouter(prefix="/api/v1", tags=["Database Related"])

@router.post("/tasks", response_model=TaskResponse)
def create_db_task(
        request: TaskCreate,
        db: Session = Depends(get_db)
):
    service = TaskService(db)
    task_id = f"Task-{uuid.uuid4()}"

    try:
        task = service.create_task(
            task_id = task_id,
            payload = request.payload,
            status = "QUEUED",
            task_type = request.type
        )
        db.commit()
        db.refresh(task)
        return orm_task_to_response(task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_db_task(
        task_id: str,
        db: Session = Depends(get_db)
):
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return orm_task_to_response(task)
