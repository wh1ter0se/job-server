import datetime as dt
from . import enums
from pathlib import Path


class Artifact:
    def save_to_file(self, path: Path):
        raise NotImplementedError("This method should be implemented by subclasses.")


class JobParameters:
    name: str
    priority: enums.JobPriority
    max_threads: int
    init_time: dt.datetime

    def __init__(
        self,
        name: str,
        priority: enums.JobPriority,
        max_threads: int,
        init_time: dt.datetime | None = None,
    ) -> None:
        self.name = name
        self.priority = priority
        self.max_threads = max_threads
        self.init_time = init_time if init_time is not None else dt.datetime.now()


class JobResult:
    return_code: enums.JobReturnCode
    artifacts: list[Artifact]

    def __init__(
        self,
        return_code: enums.JobReturnCode,
        artifacts: list[Artifact],
    ) -> None:
        self.return_code = return_code
        self.artifacts = artifacts
