from enum import Enum


class ErrorSeverity(Enum):
    WEIRD = 0
    INCONVENIENT = 1
    NOT_GOOD = 2
    VERY_NOT_GOOD = 3
    BAD = 4
    FUCKED = 5


class ErrorCode(Enum):
    UNKNOWN = 0
    DATABASE_ERROR = 1
    INPUT_FILE_MISSING = 2
    INPUT_FILE_INVALID = 3
    OUTPUT_FILE_MISSING = 4
    OUTPUT_FILE_INVALID = 5


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


class JobUpdateType(Enum):
    UNKNOWN = 0
    STATE_CHANGE = 1
    WARNING = 2
    ERROR = 3
    WEBHOOK_OPENED = 4


class ServerUpdateType(Enum):
    UNKNOWN = 0
    DATABASE = 1
    CONFIG = 2
    JOB = 3
    ARTIFACT = 4
    CLIENT = 5


class ServerUpdateSubtype:

    class Database:
        UNKNOWN = 0
        FILE_MISSING = 1
        FILE_INVALID = 2

    class Config:
        UNKNOWN = 0
        FILE_MISSING = 1
        FILE_INVALID = 2
        INVALID_KEY = 3
        INVALID_VALUE = 4

    class Job:
        UNKNOWN = 0
        STAGE_ERROR = 1
        PROCESS_ERROR = 2
        COMMAND_TIMEOUT = 3

    class Artifact:
        UNKNOWN = 0
        FILE_MISSING = 1
        FILE_INVALID = 2


class ConfigValue(Enum):
    # Paths
    CONFIG_PATH = "config_path"
    DATABASE_PATH = "database_path"

    # Preferences


class DatabaseTable(Enum):
    CONNECTION = "Connection"
    ERROR = "Error"
    JOB_STATUS = "JobStatus"
    JOB_UPDATE = "JobUpdate"
    SERVER_UPDATE = "ServerUpdate"


class SQLSetMethod(Enum):
    INSERT = 1
    UPDATE = 2
    UPSERT = 3


class SQLCompareOperator(Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
