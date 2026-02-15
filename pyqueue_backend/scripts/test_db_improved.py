"""
2026-02-15-NOTE: Have added the professional/common-practice get_db method in session.py
now I'm going to rework test_db.py to use that instead of doing "with SessionLocal() as session:...".
(Still keeping test_db.py around though for education and records' sake).
"""
# EDIT: Never mind I don't know what I was trying to do here. - get_db doesn't make sense outside of a FastAPI endpoint context.
# EDIT: Guess just playing around with writing helper methods...

import uuid
import database.models
from database.models import Task
from database.base import Base
from database.engine import engine
from database.session import SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Helper function for creating a Task and processing it w/ the session. Returns queried __repr__ string from local MySQL DB.
# DEBUG: Is it FastAPI best practice to add type hints to all parameters/fields for methods or that just for endpoint stuff? - Look into this..
def create_task(session: Session, id: str, payload: str, status: str, task_type: str) -> str | None:
    task = Task(id=id, payload=payload, status=status, task_type=task_type)
    try:
        session.add(task)
        session.commit()
        retrieve_task = session.query(Task).filter_by(id=task.id).first()
        return retrieve_task
    except IntegrityError as e:
        session.rollback()
        return str(e)
    # Don't believe that I need the finally: session.close() here? I believe I'm supposed to be calling get_db() in some form...

# Test #1:
with SessionLocal() as session:
    # Creating a Task Object:
    return_msg = create_task(session, "Task-4856593849314705", "Send en email.", "QUEUED", "EMAIL")
    print("hey look at this: ", return_msg)
