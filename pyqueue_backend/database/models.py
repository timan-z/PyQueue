from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, VARCHAR, func
from .base import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(50), primary_key = True) # primary_key ensures uniqueness so I don't need a unique=True field tacked on.
    payload = Column(Text, nullable = False)
    status = Column(String(50), nullable=False, index=True) # Remember that index should be applied to fields that'll be queried.
    task_type = Column(String(50), nullable=False, index=True)
    attempts = Column(Integer, nullable=False, default = 0) # Defaults here and below protect data integrity.
    max_retries = Column(Integer, nullable=False, default = 3)
    created_at = Column(DateTime, nullable=False, index=True, server_default=func.now())

    # Method below is for defining a developer-facing string rep of an object.
    def __repr__(self):
        return (
            f"<Task(id={self.id!r}, "   # {self.id!r} calls repr() on the value.
            f"status={self.status!r}, "
            f"task_type={self.task_type!r}, "
            f"attempts={self.attempts!r}, "
            f"max_retries={self.max_retries!r}, "
            f")>"
        )

    @property
    def is_retryable(self):
        return self.attempts >= self.max_retries
