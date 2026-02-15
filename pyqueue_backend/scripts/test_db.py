"""
Just a test file - (dated: 2026-02-14, while I'm still working with local MySQL instance pre-Docker/NGINX).
***
Test #1 - Insert Test:
- Open a session
- Create a Task Object
- Add it
- Commit it
- Query it back by id
- Print something meaningful
- Close session
***
Test #2 - Rollback Test:
- Open a session
- Create a Task Object and add it. *Don't commit*.
- Raise an exception intentionally.
- Catch it.
- Ensure that session rollback happens.
- Confirm row does NOT appear in DataBase.
(And take a look at MySQL Workbench).
***
Test #3 - Insert Duplicate ID Task Test:
- Insert duplicate ID
- Catch the exception
- Inspect the error type
- Confirm the DataBase remains consistent (no extra Task).
***
Test #4 - Generate unique ID Task Test (works everytime):
- Generate a UUID-based ID (use Python's uuid module).
- Insert Task using that ID.
- Commit it.
- Query it back.
- Print something.
"""

import uuid
import database.models
from database.models import Task
from database.base import Base
from database.engine import engine
from database.session import SessionLocal
from sqlalchemy.exc import IntegrityError

Base.metadata.create_all(bind=engine)   # No harm having it included.

# Test #1:
# Opening a session:
with SessionLocal() as session:
    # Creating a Task Object:
    task1 = Task(
        id = "Task-4856593849314705",
        payload = "Send en email.",
        status = "QUEUED",
        task_type = "EMAIL"
    )   # Rest of the fields have default values.
    # EDIT: Now that I have the try-except block below, I basically have Test #3 (inspecting duplicate addition attempt):
    try:
        session.add(task1)  # Add it.
        session.commit()    # Commit it.
        retrieve_task = session.query(Task).filter_by(id = task1.id).first()  # Query it back by id.
        print("Something meaningful: ", retrieve_task)  # Print something meaningful.
    except IntegrityError as e:
        print("Test 1 rollback about to happen.")
        print("Test 3 error inspection: ", e)
        session.rollback()
    #session.close() - NOTE: This is redundant, the session close automatically once the with statement ends!

# Test #2
with SessionLocal() as session:
    task2 = Task(
        id = "Task-idunnoman",
        payload = "Send a CRAZY email.",
        status = "QUEUED",
        task_type = "EMAIL"
    )
    session.add(task2)
    try:
        raise RuntimeError("Something went wrong!!!")
    except RuntimeError as e:
        print("Test 2 rollback about to happen.")
        session.rollback()

# Test #4 - Generating a unique ID:
with SessionLocal() as session:
    unique_id = "Task-" + str(uuid.uuid4())
    u_task = Task(
        id = unique_id,
        payload = "unique ID payload",
        status = "QUEUED",
        task_type = "EMAIL"
    )
    session.add(u_task)
    session.commit()
    retrieve_task = session.query(Task).filter_by(id=u_task.id).first()  # Query it back by id.
    print("Retrieving unique task: ", retrieve_task)  # Print something meaningful.

"""
Test #3 - Insert Duplicate ID Task Test:
- Insert duplicate ID
- Catch the exception
- Inspect the error type
- Confirm the DataBase remains consistent (no extra Task).
"""

"""
- Open a session
- Create a Task Object and add it. *Don't commit*.
- Raise an exception intentionally.
- Catch it.
- Ensure that session rollback happens.
- Confirm row does NOT appear in DataBase.
(And take a look at MySQL Workbench).
"""
