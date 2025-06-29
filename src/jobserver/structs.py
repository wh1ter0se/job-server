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
        *args,
        **kwargs,
    ) -> None:
        self.name = name
        self.priority = priority
        self.max_threads = max_threads
        self.init_time = init_time if init_time is not None else dt.datetime.now()


class JobTemplate:
    name: str
    description: str
    args: dict
    parameter_class: type[JobParameters]

    def __init__(
        self,
        name: str,
        description: str,
        args: dict,
        parameter_class: type[JobParameters],
    ) -> None:
        self.name = name
        self.description = description
        self.args = args
        self.parameter_class = parameter_class

    def fill(self, **kwargs) -> JobParameters:
        filled_args = {**self.args, **kwargs}
        return self.parameter_class(
            name=self.name,
            priority=filled_args.get("priority", enums.JobPriority.NORMAL),
            max_threads=filled_args.get("max_threads", 1),
            init_time=filled_args.get("init_time", dt.datetime.now()),
        )


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
