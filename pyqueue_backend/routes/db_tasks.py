import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from services.task_service import TaskService
from database.models import Task as OrmTask
from schemas.task import TaskResponse
from schemas.mappers import orm_task_to_response

router = APIRouter(prefix="/db", tags=["Database Tasks"])

@router.post("/tasks", response_model=TaskResponse)
def create_db_task(
        payload: str,
        task_type:str,
        db: Session = Depends(get_db)
):
    service = TaskService(db)
    task_id = f"Task-{uuid.uuid4()}"

    try:
        task = service.create_task(
            task_id = task_id,
            payload = payload,
            status = "QUEUED",
            task_type = task_type
        )
        db.commit()
        db.refresh(task)
        return orm_task_to_response(task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
