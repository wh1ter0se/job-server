# -*- coding: utf-8 -*-
import datetime as dt
from .internal import utils
from . import enums
from . import structs
from fastapi import FastAPI, APIRouter
from . import data


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
        job_id: str

        def __init__(
            self,
            name: str,
            job_id: str,
        ) -> None:
            self.name = name
            self.job_id = job_id

        def start(self) -> bool:
            return False

        def pause(self) -> bool:
            return False

        def resume(self) -> bool:
            return False

        def cancel(self) -> bool:
            return False

    # Input
    job_parameters: structs.JobParameters
    init_time: dt.datetime

    # Output
    job_status: enums.JobStatus
    job_result: structs.JobResult | None

    def __init__(self, job_parameters: structs.JobParameters):
        self.job_parameters = job_parameters
        self.job_status = enums.JobStatus.PENDING
        self.job_result = None


class JobManager:
    pass


class JobServer:

    # Data clients
    config: data.ConfigClient
    database: data.DatabaseClient

    # Internal
    _app: FastAPI
    _job_manager: JobManager

    def __init__(
        self,
        config: data.ConfigClient,
        database: data.DatabaseClient,
    ):
        self.config = config
        self.database = database

        self._app = FastAPI()
        self._job_manager = JobManager()

        raise NotImplementedError

    def _get_router(self) -> APIRouter:
        router = APIRouter()

        # Connections
        router.add_api_route("/get_connection/{client_token}", self.get_connection, methods=["GET"])
        router.add_api_route("/get_connections/", self.get_connections, methods=["GET"])

        # Errors
        router.add_api_route("/get_error/{error_id}", self.get_error, methods=["GET"])
        router.add_api_route("/get_errors/", self.get_errors, methods=["GET"])

        # Job/Server Updates
        router.add_api_route("/get_job_updates", self.get_job_updates, methods=["GET"])
        router.add_api_route("/get_server_updates", self.get_server_updates, methods=["GET"])

        # Job Control
        router.add_api_route("/start_job/", self.start_job, methods=["POST"])
        router.add_api_route("/pause_job/{job_id}", self.pause_job, methods=["POST"])
        router.add_api_route("/resume_job/{job_id}", self.resume_job, methods=["POST"])
        router.add_api_route("/cancel_job/{job_id}", self.cancel_job, methods=["POST"])
        router.add_api_route("/get_job_status/{job_id}", self.get_job_status, methods=["GET"])
        router.add_api_route("/subscribe_to_job/{job_id}", self.subscribe_to_job, methods=["GET"])

        return router

    # region Public API
    async def get_connection(
        self,
        client_token: str,
    ) -> None:
        raise NotImplementedError

    async def get_connections(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> None:
        raise NotImplementedError

    async def get_error(
        self,
        error_id: str,
        include_traceback: bool = False,
    ) -> None:
        raise NotImplementedError

    async def get_errors(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        severity_level: enums.ErrorSeverity | None = None,  # Filter
        job_id: str | None = None,  # Filter
        client_token: str | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
        include_traceback: bool = False,
    ) -> None:
        raise NotImplementedError

    async def get_job_updates(
        self,
        job_id: str | None = None,  # Filter
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> None:
        raise NotImplementedError

    async def get_server_updates(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> None:
        raise NotImplementedError

    async def start_job(
        self,
        job_parameters: dict,
    ) -> None:
        raise NotImplementedError

    async def pause_job(
        self,
        job_id: str,
    ) -> None:
        raise NotImplementedError

    async def resume_job(
        self,
        job_id: str,
    ) -> None:
        raise NotImplementedError

    async def cancel_job(
        self,
        job_id: str,
    ) -> None:
        raise NotImplementedError

    async def get_job_status(
        self,
        job_id: str,
    ) -> None:
        raise NotImplementedError

    async def subscribe_to_job(
        self,
        job_id: str,
    ) -> None:
        raise NotImplementedError

    # endregion Public API


class JobServerClient:
    pass
