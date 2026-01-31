import datetime
from pydantic import BaseModel
from enums.TaskStatus import TaskStatus
from enums.TaskType import TaskType

"""
For later documentation:
```
In PyQueue, response schemas are introduced earlier than in GoQueue and SpringQueue (base) because FastAPI strongly encourages an explicit 
separation between internal domain models and external API contracts. While the earlier base projects returned in-memory Task objects directly, 
FastAPI’s Pydantic models make response shaping, validation, and documentation first-class concerns. Introducing TaskResponse at this stage 
ensures that internal execution details (such as retry counters and max retries) remain encapsulated within the runtime, while clients interact 
only with stable, intentional representations of task state. This mirrors production-grade API design patterns and provides a natural stepping 
stone toward more advanced architectural separation later explored in SpringQueuePro.
```
"""

"""
I omitted attempts and max_retries from the response schema for Task since they represent internal retry mechanics
rather than user-relevant state (exposing them would unnecessarily couple clients to implementation details).
***
Initially I kept them and also had classConfig:\n from_attributes = True but removed it in favor of an explicit
mapper layer in schemas/mappers.py ensuring all transformations were deliberate.
"""
class TaskResponse(BaseModel):
    id: str
    payload: str
    type: TaskType
    status: TaskStatus
    created_at: datetime.datetime
