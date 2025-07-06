import os
import shutil
import pytest
import datetime as dt
import jobserver as jserv
from typing import Generator
from pathlib import Path


@pytest.fixture()
def temporary_directory() -> Generator[Path, None, None]:
    tmp_time = dt.datetime.now()
    tmp_dir = Path(f".tmp/{tmp_time.timestamp()}/")
    os.makedirs(tmp_dir, exist_ok=True)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


# region Clients
@pytest.fixture()
def config_client(temporary_directory: Path) -> Generator[jserv.ConfigClient, None, None]:
    tmp_config_path = temporary_directory.joinpath(f"config.json")
    tmp_db_path = temporary_directory.joinpath(f"jobserver.sqlite3")
    config_client = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)
    config_client.set(jserv.enums.ConfigValue.DATABASE_PATH.value, str(tmp_db_path))
    yield config_client


@pytest.fixture()
def database_client(
    config_client: jserv.ConfigClient,
) -> Generator[jserv.DatabaseClient, None, None]:
    database = jserv.DatabaseClient(config=config_client)
    yield database
    database.disconnect()


# endregion Clients


# region Database Entry Factories
class DatabaseEntryFactory:
    def get(self) -> jserv.data._DatabaseEntry:
        raise NotImplementedError


@pytest.fixture
def connection_entry_factory() -> DatabaseEntryFactory:
    class Factory(DatabaseEntryFactory):
        def get(self) -> jserv.DatabaseEntry.Connection:
            connection_entry = jserv.DatabaseEntry.Connection(
                client_token=str(hash(dt.datetime.now())),
                init_time=dt.datetime.now(),
                last_message_time=None,
                num_messages=0,
                client_ip="1.2.3.4",
            )
            return connection_entry

    return Factory()


@pytest.fixture
def error_entry_factory() -> DatabaseEntryFactory:
    class Factory(DatabaseEntryFactory):
        def get(self) -> jserv.DatabaseEntry.Error:
            error_entry = jserv.DatabaseEntry.Error(
                error_id=str(hash(dt.datetime.now())),
                error_time=dt.datetime.now(),
                severity_level=jserv.enums.ErrorSeverity.NOT_GOOD,
                traceback="",
                job_id=None,
                client_token=None,
            )
            return error_entry

    return Factory()


@pytest.fixture
def job_status_entry_factory() -> DatabaseEntryFactory:
    class Factory(DatabaseEntryFactory):
        def get(self) -> jserv.DatabaseEntry.JobStatus:
            job_status_entry = jserv.DatabaseEntry.JobStatus(
                job_id=str(hash(dt.datetime.now())),
                init_time=dt.datetime.now(),
                archived=False,
            )
            return job_status_entry

    return Factory()


@pytest.fixture
def job_update_entry_factory() -> DatabaseEntryFactory:
    class Factory(DatabaseEntryFactory):
        def get(self) -> jserv.DatabaseEntry.JobUpdate:
            job_update_entry = jserv.DatabaseEntry.JobUpdate(
                job_id=str(hash(dt.datetime.now())),
                update_time=dt.datetime.now(),
                new_state=1,
                comment="State 1 started",
            )
            return job_update_entry

    return Factory()


@pytest.fixture
def server_update_entry_factory() -> DatabaseEntryFactory:
    class Factory(DatabaseEntryFactory):
        def get(self) -> jserv.DatabaseEntry.ServerUpdate:
            server_update_entry = jserv.DatabaseEntry.ServerUpdate(
                update_time=dt.datetime.now(),
                type=1,
                subtype=1,
                comment="Server update comment",
                job_id=None,
                client_token=None,
            )
            return server_update_entry

    return Factory()


database_entry_factories = (
    "database_entry_factory_name",
    [
        ("connection_entry_factory"),
        ("error_entry_factory"),
        ("job_status_entry_factory"),
        ("job_update_entry_factory"),
        ("server_update_entry_factory"),
    ],
)

# endregion Database Entry Factories
