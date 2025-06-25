# -*- coding: utf-8 -*-
import datetime as dt
from .internal import utils
from . import enums
from . import structs


def get_hmm():
    """Get a thought."""
    return "hmmm..."


def hmm():
    """Contemplation..."""
    if utils.get_answer():
        print(get_hmm())


class Job:
    class State:
        name: str
        job_hash: str

        def __init__(
            self,
            name: str,
            job_hash: str,
        ) -> None:
            self.name = name
            self.job_hash = job_hash

        def start(self) -> bool:

            return False

        def pause(self) -> bool:
            return False

        def resume(self) -> bool:
            return False

        def cancel(self) -> bool:
            return False

    # Input parameters for the job
    job_parameters: structs.JobParameters
    init_time: dt.datetime

    # Status tracking
    job_status: enums.JobStatus

    job_result: structs.JobResult | None

    def __init__(self, job_parameters: structs.JobParameters):
        self.job_parameters = job_parameters
        self.job_status = enums.JobStatus.PENDING
        self.job_result = None


class JobManager:
    pass


class JobServer:
    pass
