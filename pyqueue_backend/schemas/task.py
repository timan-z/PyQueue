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
    type: str
    status: str
    attempts: int
    max_retries: int
    created_at: str

"""
2026-02-02-NOTE: For later documentation:
```
TaskResponse exists purely as an API-facing Data Transfer Object (DTO) and has no influence on PyQueue’s core runtime behavior. 
The internal domain model (Task) continues to use strongly-typed enums (TaskType, TaskStatus) and Python-native types to preserve correctness,
invariants, and clarity within the system.

At the API boundary, these internal representations are explicitly serialized into stable, string-based fields via task_to_response. 
Enum values are exposed using their .value (e.g., "FAILED", "EMAIL"), preserving a consistent, filterable vocabulary for clients while avoiding 
leakage of internal enum semantics. Datetime values are converted to ISO-8601 strings to establish an explicit and language-agnostic 
temporal contract.

This design mirrors established backend practices (e.g., Spring DTOs): the response schema is a compatibility layer for external consumers, 
not a driver of internal logic. As a result, the core system remains free to evolve independently of frontend or client concerns.
```
"""
# Basically TaskResponse defines the public PyQueue API. And everything else is internal.