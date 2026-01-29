from enum import Enum, auto

class TaskType(Enum):
    EMAIL = auto()
    REPORT = auto()
    DATACLEANUP = auto()
    SMS = auto()
    NEWSLETTER = auto()
    TAKESLONG = auto()
    FAIL = auto()
    FAILABS = auto()
    TEST = auto()
