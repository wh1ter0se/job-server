# -*- coding: utf-8 -*-
import datetime as dt
from . import data
from . import enums
from . import structs
from typing import Callable
from fastapi import FastAPI, APIRouter, Body


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

    def _update_state(self, new_state: enums.JobUpdateType):
        # Update the job state and call the update callback if provided
        if self._update_callback:
            self._update_callback(new_state)

        # TODO: log the job update to db
        # TODO: start the next state (if there is one and not paused)

    def get_template(self) -> dict:
        # Return the job template as a dictionary
        return {
            "name": self.parameters.name,
            "description": "Job template description",
            "args": {},
        }


class JobManager:
    def __init__(
        self,
        config: data.ConfigClient,
        database: data.DatabaseClient,
    ) -> None:
        pass

    def start(self) -> None:
        # Start the job manager
        # TODO: Implement
        pass

    def add_job(self, job: Job) -> None:
        # Add a job to the manager
        # TODO: Implement
        raise NotImplementedError()

    def get_job(self, job_id: str) -> Job | None:
        # Get a job by its ID
        # TODO: Implement
        raise NotImplementedError()

    def get_jobs(self) -> list[Job]:
        # Get all jobs managed by the manager
        # TODO: Implement
        raise NotImplementedError()

    def get_job_template(self, name: str) -> dict:
        # Get a job template by its name
        # TODO: Implement
        raise NotImplementedError()

    def get_job_templates(self) -> list[dict]:
        # Get all job templates managed by the manager
        # TODO: Implement
        raise NotImplementedError()

    def stop(self) -> None:
        # Stop the job manager
        # TODO: Implement
        raise NotImplementedError()

    def pause_all_jobs(self) -> None:
        # Pause all jobs
        # TODO: Implement
        raise NotImplementedError()

    def update_available_threads(self, available_threads: int) -> None:
        # Update the number of available threads for job processing
        # TODO: Implement
        raise NotImplementedError()


class JobServer:

    # Data clients
    config: data.ConfigClient
    database: data.DatabaseClient

    # Internal
    _init_time: dt.datetime
    _allowed_jobs: list[type[Job]]
    _router: APIRouter
    _app: FastAPI | None
    _job_manager: JobManager

    def __init__(
        self,
        config: data.ConfigClient,
        database: data.DatabaseClient,
        allowed_jobs: list[type[Job]],
        start_at_init: bool = True,
    ):
        self.config = config
        self.database = database
        self._allowed_jobs = allowed_jobs

        self._init_time = dt.datetime.now()
        self._router = self._get_router()
        self._app = None
        self._job_manager = JobManager(config=config, database=database)

        if start_at_init:
            self.start()

    def _get_router(self) -> APIRouter:
        router = APIRouter()

        # Connectivity check
        router.add_api_route("/", self.empty_response, methods=["GET", "POST"])

        # Connections
        router.add_api_route("/connection/{client_token}", self.get_connection, methods=["GET"])
        router.add_api_route("/connections/", self.get_connections, methods=["GET"])

        # Errors
        router.add_api_route("/error/{error_id}", self.get_error, methods=["GET"])
        router.add_api_route("/errors/", self.get_errors, methods=["GET"])

        # Job Templates
        router.add_api_route("/job_template/{name}", self.get_job_templates, methods=["GET"])
        router.add_api_route("/job_templates/", self.get_job_templates, methods=["GET"])

        # Job/Server Info
        router.add_api_route("/status/", self.get_server_status, methods=["GET"])
        router.add_api_route("/server_updates", self.get_server_updates, methods=["GET"])
        router.add_api_route("/active_jobs", self.get_active_jobs, methods=["GET"])
        router.add_api_route("/job_updates", self.get_job_updates, methods=["GET"])

        # Job Control
        router.add_api_route("/job/status/{job_id}", self.get_job_status, methods=["GET"])
        router.add_api_route("/job/submit/{job_id}", self.submit_job, methods=["POST"])
        router.add_api_route("/job/start/{job_id}", self.start_job, methods=["POST"])
        router.add_api_route("/job/pause/{job_id}", self.pause_job, methods=["POST"])
        router.add_api_route("/job/resume/{job_id}", self.resume_job, methods=["POST"])
        router.add_api_route("/job/cancel/{job_id}", self.cancel_job, methods=["POST"])
        router.add_api_route("/job/subscribe/{job_id}", self.subscribe_to_job, methods=["GET"])

        return router

    def start(self):
        self._app = FastAPI()
        self._app.include_router(self._router)
        self._job_manager.start()

    # region Public API
    async def empty_response(self) -> dict:
        return {}

    async def get_connection(
        self,
        client_token: str,
    ) -> dict:
        database_entry = self.database.get_entry(
            table=enums.DatabaseTable.CONNECTION,
            primary_key_fields={"client_token": client_token},
        )
        if database_entry is None:
            return {}

        connection_entry = data.DatabaseEntry.Connection(**database_entry.__dict__)
        return connection_entry.__dict__

    async def get_connections(
        self,
        client_ip: str | None = None,
        init_before: dt.datetime | None = None,  # Filter
        init_after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int | None = None,
        page: int = 1,
    ) -> list[dict]:
        filters: list[data._Filter] = []
        if init_before is not None:
            filters.append(
                data.Filter.Before(
                    time_field_name="last_message_time",
                    before_time=init_before,
                )
            )
        if init_after is not None:
            filters.append(
                data.Filter.After(
                    time_field_name="last_message_time",
                    after_time=init_after,
                )
            )
        database_entries = self.database.search_entries(
            table=enums.DatabaseTable.CONNECTION,
            filters=filters,
            limit=items_per_page,
            page=page,
        )
        if database_entries is None or len(database_entries) < 1:
            return [{}]

        connection_entries = []
        for database_entry in database_entries:
            connection_entries.append(
                data.DatabaseEntry.Connection(**database_entry.__dict__).__dict__
            )

        return connection_entries

    async def get_error(
        self,
        error_id: str,
        include_traceback: bool = False,
    ) -> dict:
        database_entry = self.database.get_entry(
            table=enums.DatabaseTable.ERROR,
            primary_key_fields={"error_id": error_id},
            skip_fields=["traceback"] if not include_traceback else [],
        )
        if database_entry is None:
            return {}

        error_entry = data.DatabaseEntry.Error(**database_entry.__dict__)
        return error_entry.__dict__

    async def get_errors(
        self,
        before: dt.datetime | None = None,  # Filter
        after: dt.datetime | None = None,  # Filter
        severity_level: enums.ErrorSeverity | None = None,  # Filter
        job_id: str | None = None,  # Filter
        client_token: str | None = None,  # Filter
        descending: bool = True,
        items_per_page: int | None = None,
        page: int = 1,
        include_traceback: bool = False,
    ) -> list[dict]:
        filters: list[data._Filter] = []
        if before is not None:
            filters.append(
                data.Filter.Before(
                    time_field_name="error_time",
                    before_time=before,
                )
            )
        if after is not None:
            filters.append(
                data.Filter.After(
                    time_field_name="error_time",
                    after_time=after,
                )
            )
        if severity_level is not None:
            filters.append(
                data.Filter.Compare(
                    field_name="severity_level",
                    operator=enums.SQLCompareOperator.EQUALS,
                    value=severity_level,
                )
            )
        if job_id is not None:
            filters.append(
                data.Filter.Compare(
                    field_name="job_id",
                    operator=enums.SQLCompareOperator.EQUALS,
                    value=job_id,
                )
            )
        if client_token is not None:
            filters.append(
                data.Filter.Compare(
                    field_name="client_token",
                    operator=enums.SQLCompareOperator.EQUALS,
                    value=client_token,
                )
            )
        database_entries = self.database.search_entries(
            table=enums.DatabaseTable.ERROR,
            filters=filters,
            limit=items_per_page,
            page=page,
        )
        if database_entries is None or len(database_entries) < 1:
            return [{}]

        error_entries = []
        for database_entry in database_entries:
            error_entries.append(data.DatabaseEntry.Error(**database_entry.__dict__).__dict__)

        return error_entries

    async def get_job_template(
        self,
        name: str,
    ) -> dict:
        return self._job_manager.get_job_template(name)

    async def get_job_templates(
        self,
        items_per_page: int | None = None,
        page: int = 1,
    ) -> list[dict]:
        return self._job_manager.get_job_templates()

    async def get_active_jobs(
        self,
        items_per_page: int = 25,
        page: int = 1,
    ) -> list[dict]:
        filters: list[data._Filter] = [
            data.Filter.Compare(
                field_name="archived",
                operator=enums.SQLCompareOperator.EQUALS,
                value=0,
            )
        ]
        database_entries = self.database.search_entries(
            table=enums.DatabaseTable.JOB_STATUS,
            filters=filters,
            limit=items_per_page,
            page=page,
        )
        if database_entries is None or len(database_entries) < 1:
            return [{}]

        job_entries = []
        for database_entry in database_entries:
            job_entries.append(data.DatabaseEntry.JobStatus(**database_entry.__dict__).__dict__)

        return job_entries

    async def get_job_updates(
        self,
        job_id: str | None = None,  # Filter
        update_before: dt.datetime | None = None,  # Filter
        update_after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int | None = None,
        page: int = 1,
    ) -> list[dict]:
        filters: list[data._Filter] = []
        if update_before is not None:
            filters.append(
                data.Filter.Before(
                    time_field_name="update_time",
                    before_time=update_before,
                )
            )
        if update_after is not None:
            filters.append(
                data.Filter.After(
                    time_field_name="update_time",
                    after_time=update_after,
                )
            )
        if job_id is not None:
            filters.append(
                data.Filter.Compare(
                    field_name="job_id",
                    operator=enums.SQLCompareOperator.EQUALS,
                    value=job_id,
                )
            )
        database_entries = self.database.search_entries(
            table=enums.DatabaseTable.JOB_UPDATE,
            filters=filters,
            limit=items_per_page,
            page=page,
        )
        if database_entries is None or len(database_entries) < 1:
            return [{}]

        job_update_entries = []
        for database_entry in database_entries:
            job_update_entries.append(
                data.DatabaseEntry.JobUpdate(**database_entry.__dict__).__dict__
            )

        return job_update_entries

    async def get_server_updates(
        self,
        update_before: dt.datetime | None = None,  # Filter
        update_after: dt.datetime | None = None,  # Filter
        descending: bool = True,
        items_per_page: int | None = None,
        page: int = 1,
    ) -> list[dict]:
        filters: list[data._Filter] = []
        if update_before is not None:
            filters.append(
                data.Filter.Before(
                    time_field_name="update_time",
                    before_time=update_before,
                )
            )
        if update_after is not None:
            filters.append(
                data.Filter.After(
                    time_field_name="update_time",
                    after_time=update_after,
                )
            )

        database_entries = self.database.search_entries(
            table=enums.DatabaseTable.SERVER_UPDATE,
            filters=filters,
            limit=items_per_page,
            page=page,
        )
        if database_entries is None or len(database_entries) < 1:
            return [{}]

        server_update_entries = []
        for database_entry in database_entries:
            server_update_entries.append(
                data.DatabaseEntry.ServerUpdate(**database_entry.__dict__).__dict__
            )

        return server_update_entries

    async def get_job_status(
        self,
        job_id: str,
    ) -> dict:
        job_status_entry = self.database.get_entry(
            table=enums.DatabaseTable.JOB_STATUS,
            primary_key_fields={"job_id": job_id},
        )
        if job_status_entry is None:
            return {}

        return data.DatabaseEntry.JobStatus(**job_status_entry.__dict__).__dict__

    async def get_server_status(
        self,
    ) -> dict:
        return {
            "status": "running",
            "init_time": self._init_time.isoformat(),
        }

    async def submit_job(
        self,
        job_id: str,
        job_parameters: dict = Body(...),
    ) -> dict:
        raise NotImplementedError()

    async def start_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError()

    async def pause_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError()

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

    async def subscribe_to_job(
        self,
        job_id: str,
    ) -> dict:
        raise NotImplementedError

    # endregion Public API


class JobServerClient:

    pass
