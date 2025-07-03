import os
import time
import shutil
import pytest
import datetime as dt
import jobserver as jserv
from enum import Enum
from typing import Generator, Callable, Any
from pathlib import Path


@pytest.fixture()
def tmp_dir() -> Generator[Path, None, None]:
    tmp_time = dt.datetime.now()
    tmp_dir = Path(f".tmp/{tmp_time.timestamp()}/")
    os.makedirs(tmp_dir, exist_ok=True)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


# region Config
def test_config_can_load(tmp_dir: Path) -> None:
    tmp_config_path = tmp_dir.joinpath(f"config.json")
    config = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)


def test_database_path_can_be_set_in_config(tmp_dir: Path) -> None:
    tmp_config_path = tmp_dir.joinpath(f"config.json")
    tmp_db_path = tmp_dir.joinpath(f"jobserver.sqlite3")
    config = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)
    config.set(jserv.enums.ConfigValue.DATABASE_PATH.value, str(tmp_db_path))


@pytest.fixture()
def config_client(tmp_dir: Path) -> Generator[jserv.ConfigClient, None, None]:
    tmp_config_path = tmp_dir.joinpath(f"config.json")
    tmp_db_path = tmp_dir.joinpath(f"jobserver.sqlite3")
    config_client = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)
    config_client.set(jserv.enums.ConfigValue.DATABASE_PATH.value, str(tmp_db_path))
    yield config_client


# endregion Config


# region Database
def test_database_client_can_load(config_client: jserv.ConfigClient) -> None:
    database = jserv.DatabaseClient(config=config_client)
    assert database


@pytest.fixture()
def database_client(
    config_client: jserv.ConfigClient,
) -> Generator[jserv.DatabaseClient, None, None]:
    database = jserv.DatabaseClient(config=config_client)
    yield database
    database.disconnect()


# endregion Databasee


# region Database - Fixtures
@pytest.fixture
def connection_entry_factory() -> object:
    class Factory:
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
def error_entry_factory() -> object:
    class Factory:
        def get(self) -> jserv.DatabaseEntry.Error:
            error_entry = jserv.DatabaseEntry.Error(
                error_id=str(hash(dt.datetime.now())),
                error_time=dt.datetime.now(),
                severity_level=jserv.enums.ErrorSeverity.NOT_GOOD,
                traceback="",
                job_hash=None,
                client_token=None,
            )
            return error_entry

    return Factory()


@pytest.fixture
def job_status_entry_factory() -> object:
    class Factory:
        def get(self) -> jserv.DatabaseEntry.JobStatus:
            job_status_entry = jserv.DatabaseEntry.JobStatus(
                job_id=str(hash(dt.datetime.now())),
                init_time=dt.datetime.now(),
                archived=False,
            )
            return job_status_entry

    return Factory()


@pytest.fixture
def job_update_entry_factory() -> object:
    class Factory:
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
def server_update_entry_factory() -> object:
    class Factory:
        def get(self) -> jserv.DatabaseEntry.ServerUpdate:
            server_update_entry = jserv.DatabaseEntry.ServerUpdate(
                time=dt.datetime.now(),
                type=1,
                subtype=1,
                comment=1,
                job_id=None,
                client_token=None,
            )
            return server_update_entry

    return Factory()


# endregion Database - Fixtures


# region Database - Helpers
class Table(Enum):
    CONNECTION = 1
    ERROR = 2
    JOB_STATUS = 3
    JOB_UPDATE = 4
    SERVER_UPDATE = 5


def set_entry(
    database_entry: Any,  # Subclass of DatabaseEntry,
    setter: Callable[
        [
            Any,  # Subclass of DatabaseEntry,
            Any,  # SQLSetMethod
        ],
        None,
    ],
    set_method: jserv.enums.SQLSetMethod,
) -> None:
    setter(database_entry, set_method)


def get_setter_for_table(
    database_client: jserv.DatabaseClient,
    table: Table,
) -> Callable[
    [
        Any,  # Subclass of DatabaseEntry,
        Any,  # SQLSetMethod
    ],
    None,
]:
    match table:
        case Table.CONNECTION:
            return database_client.set_connection_entry
        case Table.ERROR:
            return database_client.set_error_entry
        case Table.JOB_STATUS:
            return database_client.set_job_status_entry
        case Table.JOB_UPDATE:
            return database_client.set_job_update_entry
        case Table.SERVER_UPDATE:
            return database_client.set_server_update_entry
        case _:
            assert False


# endregion Database - Helpers


# region Database - Write-Only Tests


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_insert(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Insert once
    set_entry(
        database_entry=database_entry,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.INSERT,
    )


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_insert_twice_fails(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Insert once
    set_entry(
        database_entry=database_entry,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.INSERT,
    )

    # Insert twice
    with pytest.raises(Exception):
        set_entry(
            database_entry=database_entry,
            setter=setter,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_upsert_on_empty_table(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Upsert once
    set_entry(
        database_entry=database_entry,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.UPSERT,
    )


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_upsert_on_non_empty_table(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry_1 = request.getfixturevalue(database_entry_factory_name).get()
    database_entry_2 = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Insert once
    set_entry(
        database_entry=database_entry_1,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.INSERT,
    )

    # Upsert once
    set_entry(
        database_entry=database_entry_2,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.UPSERT,
    )


pytest.mark.xfail(raises=NotImplementedError)


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_update_on_empty_table(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Update once
    set_entry(
        database_entry=database_entry,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.UPDATE,
    )


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.parametrize(
    "database_entry_factory_name, table",
    [
        ("connection_entry_factory", Table.CONNECTION),
        ("error_entry_factory", Table.ERROR),
        ("job_status_entry_factory", Table.JOB_STATUS),
        ("job_update_entry_factory", Table.JOB_UPDATE),
        ("server_update_entry_factory", Table.SERVER_UPDATE),
    ],
)
def test_update_on_non_empty_table(
    database_client: jserv.DatabaseClient,
    database_entry_factory_name: str,  # Fixture -> Subclass of DatabaseEntry
    table: Table,
    request: pytest.FixtureRequest,
) -> None:
    database_entry_1 = request.getfixturevalue(database_entry_factory_name).get()
    database_entry_2 = request.getfixturevalue(database_entry_factory_name).get()
    setter = get_setter_for_table(database_client, table)

    # Insert once
    set_entry(
        database_entry=database_entry_1,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.INSERT,
    )

    # Update once
    set_entry(
        database_entry=database_entry_2,
        setter=setter,
        set_method=jserv.enums.SQLSetMethod.UPDATE,
    )


# endregion Database - Write-Only Tests


# region Database - Connection
def test_database_select_null_connection(
    database_client: jserv.DatabaseClient,
) -> None:
    connection_entry = database_client.get_connection_entry(client_token="test_token")
    assert connection_entry is None


# def test_database_insert_select_connection(
#     database_client: jserv.DatabaseClient,
#     connection_entry_factory: jserv.DatabaseEntry.Connection,
# ) -> None:
#     database_client.set_connection_entry(
#         connection_entry=connection_entry_factory,
#         set_method=jserv.enums.SQLSetMethod.INSERT,
#     )
#     retrieved_connection_entry = database_client.get_connection_entry(
#         client_token=connection_entry_factory.client_token
#     )
#     assert retrieved_connection_entry is not None
#     assert retrieved_connection_entry == connection_entry_factory


# def test_database_insert_update_select_connection(
#     database_client: jserv.DatabaseClient,
#     connection_entry_factory: jserv.DatabaseEntry.Connection,
# ) -> None:
#     database_client.set_connection_entry(
#         connection_entry=connection_entry_factory,
#         set_method=jserv.enums.SQLSetMethod.INSERT,
#     )
#     retrieved_connection_entry = database_client.get_connection_entry(
#         client_token=connection_entry_factory.client_token
#     )
#     assert retrieved_connection_entry is not None
#     assert retrieved_connection_entry == connection_entry_factory


# def test_database_upsert_select_connection(
#     database_client: jserv.DatabaseClient,
#     connection_entry: jserv.DatabaseEntry.Connection,
# ) -> None:
#     raise NotImplementedError()

# def test_database_insert_upsert_select_connection(
#     database_client: jserv.DatabaseClient,
#     connection_entry: jserv.DatabaseEntry.Connection,
# ) -> None:
#     raise NotImplementedError()

# endregion Database - Connectiopn
