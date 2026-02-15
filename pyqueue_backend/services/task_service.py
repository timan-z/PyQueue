"""
This class will be the intermediary between the routes and database.
- It will accept session in the constructor.
-- session will be stored as self.db / won't create sessions itself.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Task

class TaskService:
    # Constructor:
    def __init__(self, session_local: Session) -> None:
        self.db = session_local

    # Method for instantiating tasks:
    """
    It will:
    - Instantiate Task
    - Add
    - Commit
    - Refresh
    - Return Task Object (or an error report string being returned if some kind of error happens).
    """
    def create_task(self, task_id: str, payload: str, status: str, task_type: str) -> Task | None:
        new_task = Task(task_id=task_id, payload=payload, status=status, task_type=task_type)
        try:
            self.db.add(new_task)
            self.db.commit()
            self.db.refresh(new_task)   # I have default fields set e.g., created_at - this refresh is making sure they're set in the new_task object.
            return new_task
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise


