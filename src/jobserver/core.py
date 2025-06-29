# -*- coding: utf-8 -*-
import datetime as dt
from . import data
from . import enums
from . import structs
from typing import Callable
from fastapi import FastAPI, APIRouter


class Job:
    class State:
        name: str
        job_id: str

        def __init__(
            self,
            name: str,
            job_id: str,
            update_callback: Callable | None = None,
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
    template: type[structs.JobTemplate]
    parameters: structs.JobParameters
    init_time: dt.datetime

    # Output
    job_status: enums.JobStatus
    job_result: structs.JobResult | None

    # Internal
    _update_callback: Callable[[enums.JobUpdateType], None] | None
    _states: list[type[State]]  # List of state classes

    def __init__(
        self,
        _template: type[structs.JobTemplate],
        _states: list[type[State]],
        job_id: str | None = None,
        job_parameters: structs.JobParameters | None = None,
        update_callback: Callable[[enums.JobUpdateType], None] | None = None,
    ) -> None:
        self.template = _template
        self._states = _states
        self._update_callback = update_callback

        if job_id is not None and job_parameters is not None:
            raise ValueError("Either job_id or job_parameters should be provided, not both.")
        elif job_id is not None:
            self._load_from_memory(job_id=job_id)
        elif job_parameters is not None:
            self._create_from_parameters(job_parameters=job_parameters)
        else:
            raise ValueError("Either job_id or job_parameters must be provided.")

        self.job_status = enums.JobStatus.PENDING
        self.job_result = None

    def _load_from_memory(self, job_id: str):
        # Load job state from memory or database
        raise NotImplementedError("This method should be implemented by subclasses.")

    def _create_from_parameters(self, job_parameters: structs.JobParameters):
        # Load job state from provided parameters
        self.parameters = job_parameters

    def get_template(self) -> dict:
        # Return the job template as a dictionary
        return {
            "name": self.parameters.name,
            "description": "Job template description",
            "args": {},
        }


class JobManager:
    pass


class JobServer:

    # Data clients
    config: data.ConfigClient
    database: data.DatabaseClient

    # Internal
    _router: APIRouter
    _app: FastAPI | None
    _job_manager: JobManager

    def __init__(
        self,
        config: data.ConfigClient,
        database: data.DatabaseClient,
        start_at_init: bool = True,
    ):
        self.config = config
        self.database = database

        self._router = self._get_router()
        self._app = None
        self._job_manager = JobManager()

        if start_at_init:
            self.start()

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

    def start(self):
        self._app = FastAPI()
        self._app.include_router(self._router)

    # region Public API
    async def get_connection(
        self,
        client_token: str,
    ) -> dict:
        raise NotImplementedError

    async def get_connections(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        raise NotImplementedError

    async def get_error(
        self,
        error_id: str,
        include_traceback: bool = False,
    ) -> dict:
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
    ) -> dict:
        raise NotImplementedError

    async def get_job_templat(
        self,
        name: str,
    ) -> dict:
        raise NotImplementedError

    async def get_job_templates(
        self,
        items_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        raise NotImplementedError

    async def get_job_updates(
        self,
        job_id: str | None = None,  # Filter
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        raise NotImplementedError

    async def get_server_updates(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        raise NotImplementedError

    async def start_job(
        self,
        job_parameters: dict,
    ) -> dict:
        raise NotImplementedError

    async def pause_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    async def resume_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    async def cancel_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    async def get_job_status(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    async def subscribe_to_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    # endregion Public API


class JobServerClient:

    pass
