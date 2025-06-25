from enum import Enum


class JobPriority(Enum):
    VERY_LOW = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    VERY_HIGH = 5


class JobStatus(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    PAUSING = "Pausing"
    PAUSED = "Paused"
    RESUMING = "Resuming"
    EXITING = "Exiting"
    CLOSED = "Closed"


class JobReturnCode(Enum):
    SUCCESS = "Success"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    KILLED = "Killed"


class JobErrorCode(Enum):
    pass


class ConfigValue(Enum):
    # Paths
    CONFIG_PATH = "config_path"
    DATABASE_PATH = "database_path"

    # Preferences
