import os
import json
import shutil
import sqlite3
import datetime as dt
import importlib.resources
from enum import Enum
from typing import Any
from pathlib import Path
from . import enums

DEFAULT_CONFIG_FILE_PATH = Path(
    str(importlib.resources.files(__package__).joinpath("assets/default_config.json"))
)
DATABASE_TEMPLATE_FILE_PATH = Path(
    str(importlib.resources.files(__package__).joinpath("assets/jobserver.temp.sqlite3"))
)


class ConfigClient:

    config_file_path: Path
    create_new_if_missing: bool
    fill_missing_keys_with_defualts: bool

    _config: dict

    def __init__(
        self,
        config_file_path: Path = Path(os.getcwd()).joinpath(Path(".internal/config.json")),
        create_new_if_missing: bool = True,
        fill_missing_keys_with_defualts: bool = True,
    ):
        self.config_file_path = config_file_path
        self.create_new_if_missing = create_new_if_missing
        self.fill_missing_keys_with_defualts = fill_missing_keys_with_defualts

        self._load_config()

    def _load_default_config(self) -> dict[str, Any]:
        # Read and return the default config contents
        with open(DEFAULT_CONFIG_FILE_PATH, "r") as default_file:
            default_config: dict = json.load(default_file)
            return default_config

    def _load_config(self) -> None:
        """Load configuration from the specified JSON file."""
        # Load the existing config file
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, "r") as file:
                    self._config = json.load(file)
                self._validate_config()

            except Exception as e:
                print(f"Error loading config file {self.config_file_path}: {e}")
                raise e

        # Create new file
        elif self.create_new_if_missing:
            # TODO: Copy default location to rpovide file path
            os.makedirs(self.config_file_path.parent, exist_ok=True)
            shutil.copyfile(
                src=Path(
                    str(
                        importlib.resources.files(__package__).joinpath(
                            "assets/default_config.json"
                        )
                    )
                ),
                dst=self.config_file_path,
            )
            self._load_config()

        else:
            print(
                f"Config file {self.config_file_path} not found, and create_new_if_missing is False"
            )
            raise NotImplementedError()

    def _validate_config(self) -> None:
        default_config = self._load_default_config()
        for key in default_config.keys():
            # Check if key is in config, proceed if it is
            if key in self._config.keys():
                continue

            # Othewise, copy the missing key over (if selected)
            elif self.fill_missing_keys_with_defualts:
                self._config[key] = default_config[key]
                self._save_config()

            # Raise error if it's missing
            else:
                raise ValueError(f'Config file is missing a required key: "{key}"')

    def _save_config(self) -> None:
        """Save the current configuration to the specified JSON file."""
        try:
            with open(self.config_file_path, "w") as file:
                json.dump(self._config, file, indent=4)
        except Exception as e:
            print(f"Error saving config file {self.config_file_path}: {e}")
            raise e

    def get(self, key: str) -> Any:
        """Get a value from the configuration."""
        return self._config.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the configuration."""
        self._config[key] = value
        self._save_config()


class Filter:
    def apply(self, *args, **kwargs) -> str:
        raise NotImplementedError()


class Before(Filter):
    time_field_name: str
    before_time: dt.datetime

    def __init__(self, time_field_name: str, before_time: dt.datetime):
        self.time_field_name = time_field_name
        self.before_time = before_time

    def apply(self) -> str:
        return f"{self.time_field_name} < {int(self.before_time.timestamp() * 1e6)}"


class After(Filter):
    time_field_name: str
    after_time: dt.datetime

    def __init__(self, time_field_name: str, after_time: dt.datetime):
        self.time_field_name = time_field_name
        self.after_time = after_time

    def apply(self) -> str:
        return f"{self.time_field_name} > {int(self.after_time.timestamp() * 1e6)}"


class _DatabaseEntry:
    _table: enums.DatabaseTable
    _primary_keys: list[str]

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __eq__(self, value) -> bool:
        raise NotImplementedError("Subclasses of _DatabaseEntry must implement __eq__ method.")

    def __ne__(self, value) -> bool:
        return not self.__eq__(value)

    def _parse_timestamp(self, timestamp: str | int | float | dt.datetime) -> dt.datetime:
        # Return if already a datetime object
        if isinstance(timestamp, dt.datetime):
            return timestamp

        # Attempt to parse stringified timestamp
        elif isinstance(timestamp, str):
            # Try to parse as integer
            try:
                timestamp = int(timestamp)
            except ValueError:
                # Try to convert to float if it fails as int
                try:
                    timestamp = float(timestamp)
                except ValueError:
                    raise ValueError(f"Invalid timestamp format: {timestamp}")

        # Convert int to datetime
        if isinstance(timestamp, int):
            return dt.datetime.fromtimestamp(timestamp / 1e6)
        elif isinstance(timestamp, float):
            return dt.datetime.fromtimestamp(timestamp)
        else:
            raise ValueError(
                f"Timestamp must be a datetime, int, or float. Got {type(timestamp)} instead."
            )

    def get_fields(self, downcast: bool = True) -> dict[str, str | int | float]:
        fields: dict[str, str | int | float] = {}
        for key in self.__dict__.keys():
            if hasattr(self, key) and not key.startswith("_"):
                value = getattr(self, key)
                if value is not None:
                    if not downcast:
                        fields[key] = value
                    elif isinstance(value, dt.datetime):
                        fields[key] = int(value.timestamp() * 1e6)
                    elif isinstance(value, Enum):
                        fields[key] = value.value
                    else:
                        fields[key] = value
        return fields

    def get_table(self) -> enums.DatabaseTable:
        return self._table

    def get_primary_keys(self) -> list[str]:
        return self._primary_keys


class DatabaseEntry:
    class Connection(_DatabaseEntry):
        _table = enums.DatabaseTable.CONNECTION
        _primary_keys = ["client_token"]

        client_token: str  # Primary key
        init_time: dt.datetime
        last_message_time: dt.datetime | None
        num_messages: int
        client_ip: str

        def __init__(
            self,
            client_token: str,
            init_time: dt.datetime | int | float | str,
            last_message_time: dt.datetime | None,
            num_messages: int,
            client_ip: str,
        ) -> None:
            self.client_token = client_token
            self.init_time = self._parse_timestamp(init_time)
            self.last_message_time = (
                self._parse_timestamp(last_message_time) if last_message_time is not None else None
            )
            self.num_messages = int(num_messages)
            self.client_ip = client_ip

        def __eq__(self, value) -> bool:
            return (
                self.client_token == value.client_token
                and self.init_time == value.init_time
                and self.last_message_time == value.last_message_time
                and self.num_messages == value.num_messages
                and self.client_ip == value.client_ip
            )

    class Error(_DatabaseEntry):
        _table = enums.DatabaseTable.ERROR
        _primary_keys = ["error_id"]

        error_id: int  # Primary key
        error_time: dt.datetime
        severity_level: enums.ErrorSeverity
        traceback: str
        job_id: str | None  # FK
        client_token: str | None  # FK

        def __init__(
            self,
            error_id: int | str,
            error_time: dt.datetime | int | float | str,
            severity_level: enums.ErrorSeverity | int,
            traceback: str,
            job_id: str | None,
            client_token: str | None,
        ) -> None:
            self.error_id = int(error_id)
            self.error_time = self._parse_timestamp(error_time)
            self.severity_level = enums.ErrorSeverity(severity_level)
            self.traceback = traceback
            self.job_id = job_id
            self.client_token = client_token
            super().__init__()

        def __eq__(self, value) -> bool:
            success = True
            success &= self.error_id == value.error_id
            success &= self.error_time == value.error_time
            success &= self.severity_level == value.severity_level
            success &= self.traceback == value.traceback
            success &= self.job_id == value.job_id
            success &= self.client_token == value.client_token
            return success
            # return (
            #     self.error_id == value.error_id
            #     and self.error_time == value.error_time
            #     and self.severity_level == value.severity_level
            #     and self.traceback == value.traceback
            #     and self.job_id == value.job_hash
            #     and self.client_token == value.client_token
            # )

    class JobStatus(_DatabaseEntry):
        _table = enums.DatabaseTable.JOB_STATUS
        _primary_keys = ["job_id"]

        job_id: int  # Primary key
        init_time: dt.datetime
        archived: bool

        def __init__(
            self,
            job_id: int | str,
            init_time: dt.datetime | int | float | str,
            archived: bool,
        ) -> None:
            self.job_id = int(job_id)
            self.init_time = self._parse_timestamp(init_time)
            self.archived = archived

        def __eq__(self, value) -> bool:
            return self.job_id == value.job_id and self.init_time == value.init_time

    class JobUpdate(_DatabaseEntry):
        _table = enums.DatabaseTable.JOB_UPDATE
        _primary_keys = ["job_id", "update_time"]

        job_id: int  # Primary key
        update_time: dt.datetime  # Primary key
        new_state: int
        comment: str
        client_token: str | None  # FK
        error_id: int | None  # FK

        def __init__(
            self,
            job_id: int | str,
            update_time: dt.datetime | int | float | str,
            new_state: int | str,
            comment: str,
            client_token: str | None = None,
            error_id: int | str | None = None,
        ) -> None:
            self.job_id = int(job_id)
            self.update_time = self._parse_timestamp(update_time)
            self.new_state = int(new_state)
            self.comment = str(comment)
            self.client_token = client_token
            self.error_id = int(error_id) if error_id is not None else None

        def __eq__(self, value) -> bool:
            return (
                self.job_id == value.job_id
                and self.update_time == value.update_time
                and self.new_state == value.new_state
                and self.comment == value.comment
                and self.client_token == value.client_token
                and self.error_id == value.error_id
            )

    class ServerUpdate(_DatabaseEntry):
        _table = enums.DatabaseTable.SERVER_UPDATE
        _primary_keys = ["update_time"]

        update_time: dt.datetime  # Primary key
        type: int
        subtype: int
        comment: str
        job_id: int | None  # FK
        client_token: str | None  # FK

        def __init__(
            self,
            update_time: dt.datetime | int | float | str,
            type: int | str,
            subtype: int | str,
            comment: str,
            job_id: int | str | None,
            client_token: str | None,
        ) -> None:
            self.update_time = self._parse_timestamp(update_time)
            self.type = int(type)
            self.subtype = int(subtype)
            self.comment = str(comment)
            self.job_id = int(job_id) if job_id is not None else None
            self.client_token = client_token

        def __eq__(self, value) -> bool:
            return (
                self.update_time == value.update_time
                and self.type == value.type
                and self.subtype == value.subtype
                and self.comment == value.comment
                and self.job_id == value.job_id
                and self.client_token == value.client_token
            )


def get_database_entry_type(table: enums.DatabaseTable) -> type[_DatabaseEntry]:
    return getattr(DatabaseEntry, table.value)


class DatabaseClient:

    config: ConfigClient
    _db_connection: sqlite3.Connection

    def __init__(
        self,
        config: ConfigClient,
        create_new_if_missing: bool = True,
    ) -> None:
        self.config = config
        self._connect(create_new_if_missing=create_new_if_missing)

    def __del__(self):
        self.disconnect()

    # region Private
    def _create_new_database_file(self) -> None:
        _db_path: str = self.config.get(key=enums.ConfigValue.DATABASE_PATH.value)
        db_file_path = Path(_db_path)
        if db_file_path.exists():
            raise ValueError(f"Database file already exists: {db_file_path}")
        create_connection_table_query = """
        CREATE TABLE "Connection" (
            client_token TEXT NOT NULL,
            init_time INTEGER NOT NULL,
            last_message_time INTEGER,
            num_messages INTEGER NOT NULL, 
            client_ip TEXT NOT NULL,
            CONSTRAINT Client_PK PRIMARY KEY (client_token)
        );
        """
        generate_error_table_query = """
        CREATE TABLE Error (
            error_id INTEGER NOT NULL,
            error_time INTEGER NOT NULL,
            severity_level INTEGER NOT NULL,
            traceback TEXT,
            job_id INTEGER,
            client_token TEXT,
            CONSTRAINT Errors_PK PRIMARY KEY (error_id),
            CONSTRAINT Errors_JobStatus_FK FOREIGN KEY (job_id) REFERENCES JobStatus(job_id),
            CONSTRAINT Error_Connection_FK FOREIGN KEY (client_token) REFERENCES "Connection"(client_token)
        );          
        """
        create_job_status_table_query = """
        CREATE TABLE JobStatus (
            job_id INTEGER NOT NULL,
            init_time INTEGER NOT NULL,
            archived INTEGER NOT NULL,
            CONSTRAINT JobStatus_PK PRIMARY KEY (job_id)
        );
        """
        create_job_update_table_query = """
        CREATE TABLE JobUpdate (
            job_id INTEGER NOT NULL,
            update_time INTEGER NOT NULL,
            new_state INTEGER NOT NULL,
            comment TEXT,
            client_token TEXT,
            error_id INTEGER,
            CONSTRAINT JobUpdates_PK PRIMARY KEY (job_id,update_time),
            CONSTRAINT JobUpdate_Connection_FK FOREIGN KEY (client_token) REFERENCES "Connection"(client_token),
            CONSTRAINT JobUpdates_JobStatus_FK FOREIGN KEY (job_id) REFERENCES JobStatus(job_id),
            CONSTRAINT JobUpdate_Error_FK FOREIGN KEY (error_id) REFERENCES Error(error_id)
        );
        """
        create_server_update_table_query = """
        CREATE TABLE ServerUpdate (
            update_time INTEGER NOT NULL,
            type INTEGER NOT NULL,
            subtype INTEGER,
            comment TEXT,
            job_id INTEGER,
            client_token TEXT,
            CONSTRAINT ServerUpdates_PK PRIMARY KEY (update_time),
            CONSTRAINT ServerUpdates_JobStatus_FK FOREIGN KEY (job_id) REFERENCES JobStatus(job_id),
            CONSTRAINT ServerUpdate_Connection_FK FOREIGN KEY (client_token) REFERENCES "Connection"(client_token)
        );
        """
        self._db_connection = sqlite3.connect(db_file_path)
        cursor = self._db_connection.cursor()
        cursor.execute(create_connection_table_query)
        cursor.execute(generate_error_table_query)
        cursor.execute(create_job_status_table_query)
        cursor.execute(create_job_update_table_query)
        cursor.execute(create_server_update_table_query)
        self._db_connection.commit()

    def _connect(
        self,
        create_new_if_missing: bool,
    ) -> None:
        """Create a database connection to the SQLite database specified by db_file."""
        try:
            _db_path: str = self.config.get(key=enums.ConfigValue.DATABASE_PATH.value)
            db_file_path = Path(_db_path)
            if db_file_path.exists():
                # Connect to existing database
                self._db_connection = sqlite3.connect(db_file_path)
            elif create_new_if_missing:
                # Create a new database file
                self._create_new_database_file()
            else:
                # Raise an error if the database file does not exist
                raise FileNotFoundError(f"Database file does not exist: {db_file_path}")
                # shutil.copyfile(src=DATABASE_TEMPLATE_FILE_PATH, dst=db_file_path)
            print(f"Connected to database: {db_file_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise e

    # endregion Private

    # region Public

    def disconnect(self) -> None:
        self._db_connection.close()

    def set_entry(
        self,
        entry: _DatabaseEntry,
        set_method: enums.SQLSetMethod,
    ) -> None:
        entries = entry.get_fields()
        columns = list(entries.keys())
        values = list(entries.values())

        primary_keys = entry.get_primary_keys()

        table_name = entry.get_table().value

        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO {} ({}) VALUES ({})".format(
                    table_name,
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE {} SET {} WHERE {}".format(
                    table_name,
                    ", ".join(f"{column} = ?" for column in columns if column not in primary_keys),
                    " AND ".join(f"{column} = ?" for column in primary_keys),
                )
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}".format(
                    table_name,
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(primary_keys),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}"
                        for column in columns
                        if column not in primary_keys
                    ),
                )

        # Execute the query and commit the changes
        cursor = self._db_connection.cursor()
        cursor.execute(query, values)
        self._db_connection.commit()

    def get_entry(
        self,
        table: enums.DatabaseTable,
        primary_key_fields: dict[str, str | int | float],
        skip_fields: list[str] = [],
    ) -> _DatabaseEntry | None:
        database_entry_type = get_database_entry_type(table=table)
        table = database_entry_type._table
        columns = {_ for _ in database_entry_type.__annotations__.keys()}

        for field in skip_fields:
            columns.remove(field)

        query = "SELECT {} FROM {} WHERE {}".format(
            ", ".join(columns),
            table.value,
            " AND ".join(f"{key} = ?" for key in primary_key_fields.keys()),
        )

        try:
            cursor = self._db_connection.cursor()
            cursor.execute(query, list(primary_key_fields.values()))

            kwargs = {}
            row = cursor.fetchone()
            if row is None:
                return None

            for column, value in zip(columns, row):
                kwargs[column] = value
            database_entry = database_entry_type(**kwargs)
            return database_entry
        except sqlite3.Error as e:
            print(f"Error getting entry: {e}")
            return None

    def search_entries(
        self,
        table: enums.DatabaseTable,
        filters: list[Filter] = [],
        limit: int = 0,
        page: int = 0,
    ) -> list[_DatabaseEntry] | None:
        conditions = [filter.apply() for filter in filters]
        parameters = []
        if limit > 0:
            conditions.append("LIMIT ?")
            parameters.append(limit)
        if page > 0:
            offset = page * limit
            conditions.append("OFFSET ?")
            parameters.append(offset)

        query = f"SELECT * FROM {table.value} "
        query += " AND ".join(conditions)

        cursor = self._db_connection.cursor()
        query_result = cursor.execute(query, parameters)

        retrieved_entries = []
        for row in query_result.fetchall():
            kwargs = {key: value for key, value in zip(query_result.description, row)}
            database_entry = get_database_entry_type(table=table)(**kwargs)
            retrieved_entries.append(database_entry)

        return retrieved_entries

    def search_connection_entries(
        self,
        before: dt.datetime | None = None,
        after: dt.datetime | None = None,
        limit: int = 0,
        offset: int = 0,
    ) -> list[DatabaseEntry.Connection] | None:
        cursor = self._db_connection.cursor()
        conditions: list[str] = []
        parameters: list[str] = []
        if before is not None:
            conditions.append("init_time < ?")
        if after is not None:
            conditions.append("init_time > ?")
        if limit > 0:
            conditions.append("LIMIT ?")
        if offset > 0:
            conditions.append("OFFSET ?")

        query = "SELECT * FROM Connection"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query_result = cursor.execute(query, parameters)
        connection_entries = []
        for row in query_result.fetchall():
            # Create a DatabaseEntry.Connection object from the row
            connection_entry = DatabaseEntry.Connection(
                client_token=row[0],
                init_time=dt.datetime.fromtimestamp(row[1]),
                last_message_time=(dt.datetime.fromtimestamp(row[2]) if row[2] else None),
                num_messages=row[3],
                client_ip=row[4],
            )

            connection_entries.append(connection_entry)

        return connection_entries if len(connection_entries) > 0 else None

    # endregion Public
