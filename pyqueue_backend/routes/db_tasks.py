import uuid
import logging
import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.session import get_db
from services.task_service import TaskService
from database.models import Task as OrmTask
from schemas.task import TaskResponse
from schemas.task import TaskCreate
from schemas.mappers import orm_task_to_response

router = APIRouter(prefix="/api/v1", tags=["Database Related"])

logger = logging.getLogger(__name__)

"""Create a new persisted task."""
@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_db_task(
        request: TaskCreate,
        db: Session = Depends(get_db)
):
    service = TaskService(db)
    task_id = f"Task-{uuid.uuid4()}"
    logger.info("LOGGER: Creating task", extra={"task_id": task_id})

    try:
        task = service.create_task(
            task_id = task_id,
            payload = request.payload,
            status = "QUEUED",
            task_type = request.task_type
        )
        db.commit()
        db.refresh(task)
        return orm_task_to_response(task)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate Task")
    except Exception as e:
        # SENTRY-LEARNING: Going to adjust this one so it's caught by Sentry now.
        db.rollback()
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

"""Retrieve a specific persisted task."""
@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_db_task(
        task_id: str,
        db: Session = Depends(get_db)
):
    logger.info("LOGGER: Retrieving task", extra={"task_id": task_id})
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task for retrieval not found")
    return orm_task_to_response(task)

"""Get a list of persisted tasks."""
@router.get("/tasks", response_model=list[TaskResponse], status_code=200)
def get_db_tasks(db: Session = Depends(get_db)):
    logger.info("LOGGER: Retrieving ALL tasks")
    service = TaskService(db)
    tasks = service.get_tasks()
    return [orm_task_to_response(t) for t in tasks]

"""Delete a task that is currently persisted."""
# Unsure about the response_model for this one - thinking about returning a Task rep of the deleted task but not sure?
@router.delete("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def delete_db_task(
        task_id: str,
        db: Session = Depends(get_db)
):
    logger.info("LOGGER: Deleting task", extra={"task_id": task_id})
    service = TaskService(db)
    task = service.delete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task for deletion not found")
    db.commit()
    return orm_task_to_response(task)
