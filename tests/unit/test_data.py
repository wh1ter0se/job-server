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
@pytest.mark.dependency()
def test_config_can_load(tmp_dir: Path) -> None:
    tmp_config_path = tmp_dir.joinpath(f"config.json")
    config = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)


@pytest.mark.dependency()
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
@pytest.mark.dependency(
    depends=[
        "test_config_can_load",
        "test_database_path_can_be_set_in_config",
    ]
)
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


# region Database - Database Entry Factories
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


# endregion Database - Database Entry Factories


# region Database - Helpers
def set_entry(
    database_entry: jserv.data._DatabaseEntry,
    setter: Callable[
        [
            jserv.data._DatabaseEntry,
            jserv.enums.SQLSetMethod,
        ],
        None,
    ],
    set_method: jserv.enums.SQLSetMethod,
) -> None:
    setter(database_entry, set_method)


def get_setter_for_table(
    database_client: jserv.DatabaseClient,
    table: jserv.enums.DatabaseTable,
) -> Callable[
    [
        Any,  # Subclass of DatabaseEntry,
        Any,  # SQLSetMethod
    ],
    None,
]:
    match table:
        case jserv.enums.DatabaseTable.CONNECTION:
            return database_client.set_connection_entry
        case jserv.enums.DatabaseTable.ERROR:
            return database_client.set_error_entry
        case jserv.enums.DatabaseTable.JOB_STATUS:
            return database_client.set_job_status_entry
        case jserv.enums.DatabaseTable.JOB_UPDATE:
            return database_client.set_job_update_entry
        case jserv.enums.DatabaseTable.SERVER_UPDATE:
            return database_client.set_server_update_entry
        case _:
            assert False


# endregion Database - Test Suites


# region Database - Test Suites
database_entry_facory_parameters = (
    "database_entry_factory_name",
    [
        ("connection_entry_factory"),
        ("error_entry_factory"),
        ("job_status_entry_factory"),
        ("job_update_entry_factory"),
        ("server_update_entry_factory"),
    ],
)


@pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseSetFunctions:
    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_insert(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_insert_twice_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Insert twice
        with pytest.raises(Exception):
            database_client.set_entry(
                entry=database_entry,
                set_method=jserv.enums.SQLSetMethod.INSERT,
            )

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_upsert_on_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Upsert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.UPSERT,
        )

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_upsert_on_non_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Upsert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.UPSERT,
        )

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_update_on_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Update once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.UPDATE,
        )

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_update_on_non_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Update once
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.UPDATE,
        )


# @pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseGetFunctions:
    parameters = ("database_entry_factory_name, table",)

    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_get_on_empty_table_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Get entry's primary key(s)
        primary_key_fields = {
            key: val
            for key, val in database_entry.get_fields().items()
            if key in database_entry.get_primary_keys()
        }

        # Get entry from database by PK
        with pytest.raises(Exception):
            retrieved_entry = database_client.get_entry(
                table=database_entry.get_table(),
                primary_key_fields=primary_key_fields,
            )
            assert retrieved_entry is not None

    @pytest.mark.xfail()
    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_get_on_empty_record_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry_1 = database_entry_factory.get()
        database_entry_2 = database_entry_factory.get()

        # Ensure entries are different
        assert database_entry_1.get_table() == database_entry_2.get_table()
        assert database_entry_1 != database_entry_2

        # Set new entry
        database_client.set_entry(
            entry=database_entry_1,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Get a different entry's primary key(s)
        primary_key_fields = {
            key: val
            for key, val in database_entry_2.get_fields().items()
            if key in database_entry_2.get_primary_keys()
        }

        # Get second entry from database by PK
        database_client.get_entry(
            table=database_entry_2.get_table(),
            primary_key_fields=primary_key_fields,
        )

    @pytest.mark.xfail()
    @pytest.mark.parametrize(*database_entry_facory_parameters)
    def test_get_on_non_empty_record(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,  # Fixture -> DatabaseEntryFactory -> jserv.data._DatabaseEntry
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Set new entry
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Get entry's primary key(s)
        primary_key_fields = {
            key: val
            for key, val in database_entry.get_fields().items()
            if key in database_entry.get_primary_keys()
        }

        # Get entry from database by PK
        retrieved_entry = database_client.get_entry(
            table=database_entry.get_table(),
            primary_key_fields=primary_key_fields,
        )

        assert retrieved_entry is not None
        assert retrieved_entry == database_entry


@pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseSearchFunctions:
    @pytest.mark.xfail()
    def test_search_by_primary_key(self) -> None:
        pass

    @pytest.mark.xfail()
    def test_search_by_non_primary_key(self) -> None:
        pass


# endregion Database - Test Suites


# region Database - Connection
# def test_database_select_null_connection(
#     database_client: jserv.DatabaseClient,
# ) -> None:
#     connection_entry = database_client.get_connection_entry(client_token="test_token")
#     assert connection_entry is None


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
