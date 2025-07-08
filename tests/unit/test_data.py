import pytest
import datetime as dt
import jobserver as jserv
from pathlib import Path
from tests.fixtures.clients import (  # type:ignore
    temporary_directory,
    config_client,
    database_client,
)
from tests.fixtures.database_entry_factories import (  # type:ignore
    connection_entry_factory,
    error_entry_factory,
    job_status_entry_factory,
    job_update_entry_factory,
    server_update_entry_factory,
    DatabaseEntryFactory,
    database_entry_factory_parameters,
)


@pytest.mark.dependency()
class TestConfigClientBasicFunctionality:
    @pytest.mark.dependency()
    def test_config_can_load(self, temporary_directory: Path) -> None:
        tmp_config_path = temporary_directory.joinpath(f"config.json")
        config = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)
        assert config is not None

    @pytest.mark.dependency(
        name="test_database_path_can_be_set_in_config",
        depends=["test_config_can_load"],
        scope="class",
    )
    def test_database_path_can_be_set_in_config(self, temporary_directory: Path) -> None:
        tmp_config_path = temporary_directory.joinpath(f"config.json")
        tmp_db_path = temporary_directory.joinpath(f"jobserver.sqlite3")
        config = jserv.ConfigClient(config_file_path=tmp_config_path, create_new_if_missing=True)
        assert config is not None
        config.set(jserv.enums.ConfigValue.DATABASE_PATH.value, str(tmp_db_path))


@pytest.mark.dependency(depends=["test_database_path_can_be_set_in_config"])
class TestDatabaseClientBasicFunctionality:
    @pytest.mark.dependency(name="test_database_client_can_load")
    def test_database_client_can_load(self, config_client: jserv.ConfigClient) -> None:
        database = jserv.DatabaseClient(config=config_client)
        assert database


@pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseSetFunctions:
    @pytest.mark.dependency(name="test_insert")
    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_insert(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_insert_twice_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_upsert_on_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_upsert_on_non_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_update_on_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_update_on_non_empty_table(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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


@pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseGetFunctions:
    parameters = ("database_entry_factory_name, table",)

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_get_on_empty_table_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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
    @pytest.mark.parametrize(*database_entry_factory_parameters)
    @pytest.mark.dependency(depends=["test_insert"])
    def test_get_on_empty_record_fails(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
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

        # Insert new entry
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
        retrieved_entry = database_client.get_entry(
            table=database_entry_2.get_table(),
            primary_key_fields=primary_key_fields,
        )
        assert retrieved_entry is None

    @pytest.mark.parametrize(*database_entry_factory_parameters)
    @pytest.mark.dependency(depends=["test_insert"])
    def test_get_on_non_empty_record(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert new entry
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

    @pytest.mark.xfail()
    @pytest.mark.parametrize(*database_entry_factory_parameters)
    def test_get_on_multiple_records(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )

        # Create two different entries
        database_entry_1 = database_entry_factory.get()
        database_entry_2 = database_entry_factory.get()

        # Ensure entries are different
        assert database_entry_1 != database_entry_2

        # Insert both entries
        database_client.set_entry(
            entry=database_entry_1,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )
        database_client.set_entry(
            entry=database_entry_2,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Get first entry from database by PK
        retrieved_entry_1 = database_client.get_entry(
            table=database_entry_1.get_table(),
            primary_key_fields={
                key: val
                for key, val in database_entry_1.get_fields().items()
                if key in database_entry_1.get_primary_keys()
            },
        )
        assert retrieved_entry_1 is not None
        assert retrieved_entry_1 == database_entry_1

        # Get second entry from database by PK
        retrieved_entry_2 = database_client.get_entry(
            table=database_entry_2.get_table(),
            primary_key_fields={
                key: val
                for key, val in database_entry_2.get_fields().items()
                if key in database_entry_2.get_primary_keys()
            },
        )
        assert retrieved_entry_2 is not None
        assert retrieved_entry_2 == database_entry_2


# @pytest.mark.dependency(depends=["test_database_client_can_load"])
class TestDatabaseSearchFunctions:
    time_field_parameters = (
        "database_entry_factory_name,time_field_name",
        [
            ("connection_entry_factory", "init_time"),
            ("error_entry_factory", "error_time"),
            ("job_status_entry_factory", "init_time"),
            ("job_update_entry_factory", "update_time"),
            ("server_update_entry_factory", "update_time"),
        ],
    )

    @pytest.mark.parametrize(*time_field_parameters)
    def test_search_with_before_filter(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        time_field_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert new entry
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Calculate before/after timestamps
        fields = database_entry.get_fields(downcast=False)
        time_field = fields[time_field_name]
        assert isinstance(time_field, dt.datetime)
        before_timestamp: dt.datetime = time_field - dt.timedelta(days=1)
        after_timestamp: dt.datetime = time_field + dt.timedelta(days=1)

        # Search for entry using filter before entry
        before_entries = database_client.search_entries(
            database_entry.get_table(),
            filters=[
                jserv.data.Filter.Before(
                    time_field_name=time_field_name,
                    before_time=before_timestamp,
                )
            ],
        )
        assert before_entries is None or len(before_entries) == 0

        # Search for entry using filter after entry
        after_entries = database_client.search_entries(
            database_entry.get_table(),
            filters=[
                jserv.data.Filter.Before(
                    time_field_name=time_field_name,
                    before_time=after_timestamp,
                )
            ],
        )
        assert after_entries is not None
        assert len(after_entries) == 1
        assert after_entries[0] == database_entry

    @pytest.mark.parametrize(*time_field_parameters)
    def test_search_with_after_filter(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        time_field_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert new entry
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Calculate before/after timestamps
        fields = database_entry.get_fields(downcast=False)
        time_field = fields[time_field_name]
        assert isinstance(time_field, dt.datetime)
        before_timestamp: dt.datetime = time_field - dt.timedelta(days=1)
        after_timestamp: dt.datetime = time_field + dt.timedelta(days=1)

        # Search for entry using filter after entry
        after_entries = database_client.search_entries(
            database_entry.get_table(),
            filters=[
                jserv.data.Filter.After(
                    time_field_name=time_field_name,
                    after_time=after_timestamp,
                )
            ],
        )
        assert after_entries is None or len(after_entries) == 0

        # Search for entry using filter before entry
        before_entries = database_client.search_entries(
            database_entry.get_table(),
            filters=[
                jserv.data.Filter.After(
                    time_field_name=time_field_name,
                    after_time=before_timestamp,
                )
            ],
        )
        assert before_entries is not None
        assert len(before_entries) == 1
        assert before_entries[0] == database_entry

    @pytest.mark.parametrize(*time_field_parameters)
    def test_search_with_before_and_after_filter(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        time_field_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert new entry
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

        # Calculate before/after timestamps
        fields = database_entry.get_fields(downcast=False)
        time_field = fields[time_field_name]
        assert isinstance(time_field, dt.datetime)
        before_timestamp: dt.datetime = time_field - dt.timedelta(days=1)
        after_timestamp: dt.datetime = time_field + dt.timedelta(days=1)

        # Search for entry using filter before and after entry
        between_entries = database_client.search_entries(
            database_entry.get_table(),
            filters=[
                jserv.data.Filter.After(
                    time_field_name=time_field_name,
                    after_time=before_timestamp,
                ),
                jserv.data.Filter.Before(
                    time_field_name=time_field_name,
                    before_time=after_timestamp,
                ),
            ],
        )
        assert between_entries is not None
        assert len(between_entries) == 1
        assert between_entries[0] == database_entry

    @pytest.mark.parametrize(
        "database_entry_factory_name,key_name",
        [
            ("connection_entry_factory", "client_ip"),
            ("error_entry_factory", "severity_level"),
            ("job_status_entry_factory", "new_state"),
            ("job_update_entry_factory", "update_time"),
            ("server_update_entry_factory", "update_time"),
        ],
    )
    def test_search_by_exact_match(
        self,
        database_client: jserv.DatabaseClient,
        database_entry_factory_name: str,
        key_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        database_entry_factory: DatabaseEntryFactory = request.getfixturevalue(
            database_entry_factory_name
        )
        database_entry = database_entry_factory.get()

        # Insert new entry
        database_client.set_entry(
            entry=database_entry,
            set_method=jserv.enums.SQLSetMethod.INSERT,
        )

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_search_by_less_than(
        self,
        request: pytest.FixtureRequest,
    ) -> None:
        raise NotImplementedError()

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_search_by_less_than_or_equal_to(
        self,
        request: pytest.FixtureRequest,
    ) -> None:
        raise NotImplementedError()

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_search_by_greater_than(
        self,
        request: pytest.FixtureRequest,
    ) -> None:
        raise NotImplementedError()

    @pytest.mark.xfail(raises=NotImplementedError)
    def test_search_by_greater_than_or_equal_to(
        self,
        request: pytest.FixtureRequest,
    ) -> None:
        raise NotImplementedError()
