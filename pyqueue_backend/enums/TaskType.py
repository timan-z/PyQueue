from enum import Enum

"""
2026-01-31:
Each enum was originally instantiated with auto() but that auto-assigns them integers and so it basically goes 1,2,3, and onwards.
For API-facing enums (here), it's best practice to have string enums instead of auto() so clients can send readable strings.
- Realized this issue when Postman testing my Phase 2 implementation of this project: "EMAIL" not getting recognized for enqueueing new tasks.
- FastAPI's OpenAPI docs look much cleaner this way too (and of course makes the later frontend integration much easier).
"""
class TaskType(str, Enum):
    EMAIL = "EMAIL"
    REPORT = "REPORT"
    DATACLEANUP = "DATACLEANUP"
    SMS = "SMS"
    NEWSLETTER = "NEWSLETTER"
    TAKESLONG = "TAKESLONG"
    FAIL = "FAIL"
    FAILABS = "FAILABS"
    TEST = "TEST"
