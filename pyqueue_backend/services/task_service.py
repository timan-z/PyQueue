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
            # EDIT: Smarter to have commit() + refresh() outside of here - something I should practice given I'll be in fintech soon.
            #self.db.commit()
            #self.db.refresh(new_task)   # I have default fields set e.g., created_at - this refresh is making sure they're set in the new_task object.
            return new_task
        except IntegrityError:
            raise
        except Exception:
            raise

    def get_task(self, task_id: str) -> Task | None:
        return self.db.query(Task).filter_by(task_id=task_id).first()

    def get_tasks(self) -> list[Task]:
        return self.db.query(Task).all()

    # Not sure if task deletion should return a Task, a string message, or nothing?
    def delete_task(self, task_id: str) -> Task | None:
        task = self.db.query(Task).filter_by(task_id=task_id).first() #And task_id should be unique in the table so no need for first() or anything like that.
        if not task:
            return None
        self.db.delete(task)
        return task