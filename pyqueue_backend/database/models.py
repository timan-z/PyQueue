from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, VARCHAR
from .base import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(50), primary_key = True) # primary_key ensures uniqueness so I don't need a unique=True field tacked on.
    payload = Column(Text, nullable = False)
    status = Column(VARCHAR(50), nullable=False, index=True) # Remember that index should be applied to fields that'll be queried.
    task_type = Column(VARCHAR(50), nullable=False, index=True)
    attempts = Column(Integer, nullable=False, default = 0) # Defaults here and below protect data integrity.
    max_retries = Column(Integer, nullable=False, default = 3)
    created_at = Column(DateTime, nullable=False, index=True)
