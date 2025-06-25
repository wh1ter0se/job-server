from enum import Enum

class JobPriority(Enum):
    VERY_LOW = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    VERY_HIGH = 5

class JobReturnCode(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    CANCELLED = "Cancelled"
    KILLED = "Killed"