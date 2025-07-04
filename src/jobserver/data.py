import os
import json
import shutil
import sqlite3
import datetime as dt
import importlib.resources
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


class _DatabaseEntry:
    _table: enums.DatabaseTable
    _primary_keys: list[str]

    def __init__(
        self,
        table: enums.DatabaseTable,
        primary_keys: list[str],
    ) -> None:
        self._table = table
        self._primary_keys = primary_keys

    def __eq__(self, value) -> bool:
        raise NotImplementedError("Subclasses of _DatabaseEntry must implement __eq__ method.")

    def get_fields(self) -> dict[str, str | int | float]:
        fields: dict[str, str | int | float] = {}
        for key in self.__dict__.keys():
            if hasattr(self, key) and not key.startswith("_"):
                value = getattr(self, key)
                if value is not None:
                    if isinstance(value, dt.datetime):
                        fields[key] = int(value.timestamp() * 1e6)
                    elif isinstance(value, enums.ErrorSeverity):
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
        client_token: str  # Primary key
        init_time: dt.datetime
        last_message_time: dt.datetime | None
        num_messages: int
        client_ip: str

        def __init__(
            self,
            client_token: str,
            init_time: dt.datetime,
            last_message_time: dt.datetime | None,
            num_messages: int,
            client_ip: str,
        ) -> None:
            self.client_token = client_token
            self.init_time = init_time
            self.last_message_time = last_message_time
            self.num_messages = num_messages
            self.client_ip = client_ip
            super().__init__(
                table=enums.DatabaseTable.CONNECTION,
                primary_keys=["client_token"],
            )

        def __eq__(self, value) -> bool:
            return (
                self.client_token == value.client_token
                and self.init_time == value.init_time
                and self.last_message_time == value.last_message_time
                and self.num_messages == value.num_messages
                and self.client_ip == value.client_ip
            )

    class Error(_DatabaseEntry):
        error_id: str  # Primary key
        error_time: dt.datetime
        severity_level: enums.ErrorSeverity
        traceback: str
        job_id: str | None  # FK
        client_token: str | None  # FK

        def __init__(
            self,
            error_id: str,
            error_time: dt.datetime,
            severity_level: enums.ErrorSeverity,
            traceback: str,
            job_id: str | None,
            client_token: str | None,
        ) -> None:
            self.error_id = error_id
            self.error_time = error_time
            self.severity_level = severity_level
            self.traceback = traceback
            self.job_id = job_id
            self.client_token = client_token
            super().__init__(
                table=enums.DatabaseTable.ERROR,
                primary_keys=["error_id"],
            )

        def __eq__(self, value) -> bool:
            return (
                self.error_id == value.error_id
                and self.error_time == value.error_time
                and self.severity_level == value.severity_level
                and self.traceback == value.traceback
                and self.job_id == value.job_hash
                and self.client_token == value.client_token
            )

    class JobStatus(_DatabaseEntry):
        job_id: str  # Primary key
        init_time: dt.datetime
        archived: bool

        def __init__(
            self,
            job_id: str,
            init_time: dt.datetime,
            archived: bool,
        ) -> None:
            self.job_id = job_id
            self.init_time = init_time
            self.archived = archived
            super().__init__(
                table=enums.DatabaseTable.JOB_STATUS,
                primary_keys=["job_id"],
            )

        def __eq__(self, value) -> bool:
            return self.job_id == value.job_id and self.init_time == value.init_time

    class JobUpdate(_DatabaseEntry):
        job_id: str  # Primary key
        update_time: dt.datetime  # Primary key
        new_state: int
        comment: str
        client_token: str | None  # FK
        error_id: str | None  # FK

        def __init__(
            self,
            job_id: str,
            update_time: dt.datetime,
            new_state: int,
            comment: str,
            client_token: str | None = None,
            error_id: str | None = None,
        ) -> None:
            self.job_id = job_id
            self.update_time = update_time
            self.new_state = new_state
            self.comment = comment
            self.client_token = client_token
            self.error_id = error_id
            super().__init__(
                table=enums.DatabaseTable.JOB_UPDATE,
                primary_keys=["job_id", "update_time"],
            )

        def __eq__(self, value) -> bool:
            return (
                self.job_id == value.job_id
                and self.update_time == value.update_time
                and self.new_state == value.new_state
                and self.comment == value.comment
            )

    class ServerUpdate(_DatabaseEntry):
        update_time: dt.datetime  # Primary key
        type: int
        subtype: int
        comment: str
        job_id: str | None  # FK
        client_token: str | None  # FK

        def __init__(
            self,
            update_time: dt.datetime,
            type: int,
            subtype: int,
            comment: str,
            job_id: str | None,
            client_token: str | None,
        ) -> None:
            self.update_time = update_time
            self.type = type
            self.subtype = subtype
            self.comment = comment
            self.job_id = job_id
            self.client_token = client_token
            super().__init__(
                table=enums.DatabaseTable.SERVER_UPDATE,
                primary_keys=["update_time"],
            )

        def __eq__(self, value) -> bool:
            return (
                self.update_time == value.time
                and self.type == value.type
                and self.subtype == value.subtype
                and self.comment == value.comment
                and self.job_id == value.job_id
                and self.client_token == value.client_token
            )


class DatabaseClient:

    config: ConfigClient
    _db_connection: sqlite3.Connection

    def __init__(self, config: ConfigClient):
        self.config = config
        self._connect()

    def __del__(self):
        self.disconnect()

    # region Private
    def _connect(self) -> None:
        """Create a database connection to the SQLite database specified by db_file."""
        try:
            _db_path: str = self.config.get(key=enums.ConfigValue.DATABASE_PATH.value)
            db_file_path = Path(_db_path)
            if not db_file_path.exists():
                shutil.copyfile(src=DATABASE_TEMPLATE_FILE_PATH, dst=db_file_path)
            self._db_connection = sqlite3.connect(db_file_path)
            print(f"Connected to database: {db_file_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise e

    def disconnect(self) -> None:
        self._db_connection.close()

    # endregion Private

    # region Public
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

    # region Connection
    def get_connection_entry(
        self,
        client_token: str,
    ) -> DatabaseEntry.Connection | None:
        cursor = self._db_connection.cursor()
        query_result = cursor.execute(
            "SELECT * FROM Connection WHERE client_token = ?", (client_token,)
        )
        row = query_result.fetchone()
        if row is None:
            return None

        # Create a DatabaseEntry.Connection object from the row
        connection_entry = DatabaseEntry.Connection(
            client_token=row[0],
            init_time=dt.datetime.fromtimestamp(row[1]),
            last_message_time=(dt.datetime.fromtimestamp(row[2]) if row[2] else None),
            num_messages=row[3],
            client_ip=row[4],
        )

        return connection_entry

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

    def set_connection_entry(
        self,
        connection_entry: DatabaseEntry.Connection,
        set_method: enums.SQLSetMethod = enums.SQLSetMethod.INSERT,
    ) -> None:
        # Get the columns and values from the connection object
        columns = [
            "client_token",
            "init_time",
            "num_messages",
            "client_ip",
        ]
        values = [
            connection_entry.client_token,
            connection_entry.init_time.timestamp(),
            connection_entry.num_messages,
            connection_entry.client_ip,
        ]

        # If the last_message_time is set, add it to the columns and values
        if connection_entry.last_message_time is not None:
            columns.append("last_message_time")
            values.append(connection_entry.last_message_time.timestamp())

        # Construct the query based on the set method
        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO Connection ({}) VALUES ({})".format(
                    ", ".join(columns), ", ".join("?" * len(columns))
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE Connection SET {} WHERE client_token = ?".format(
                    ", ".join(f"{column} = ?" for column in columns if column != "client_token")
                )
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO Connection ({}) VALUES ({}) ON CONFLICT (client_token) DO UPDATE SET {}".format(
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}"
                        for column in columns
                        if column != "client_token"
                    ),
                )

        # Execute the query and commit the changes
        cursor = self._db_connection.cursor()
        cursor.execute(query, values)
        self._db_connection.commit()

    # endregion Connection

    # region   Error
    def get_error_entry(
        self,
        error_id: str,
    ) -> DatabaseEntry.Error | None:
        raise NotImplementedError

    def set_error_entry(
        self,
        error_entry: DatabaseEntry.Error,
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        # Get the columns and values from the error_entry object
        columns = [
            "error_id",
            "error_time",
            "severity_level",
            "traceback",
            "job_id",
            "client_token",
        ]
        values = [
            error_entry.error_id,
            error_entry.error_time.timestamp(),
            error_entry.severity_level.value,
            error_entry.traceback,
            error_entry.job_id,
            error_entry.client_token,
        ]

        # Construct the query based on the set method
        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO Error ({}) VALUES ({})".format(
                    ", ".join(columns), ", ".join("?" * len(columns))
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE Error SET {} WHERE error_id = ?".format(
                    ", ".join(f"{column} = ?" for column in columns if column != "error_id")
                )
                # values.append(error_entry.error_id)
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO Error ({}) VALUES ({}) ON CONFLICT (error_id) DO UPDATE SET {}".format(
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}"
                        for column in columns
                        if column != "error_id"
                    ),
                )

        # Execute the query and commit the changes
        cursor = self._db_connection.cursor()
        cursor.execute(query, values)
        self._db_connection.commit()

    # endregion Error

    # region   Job Status
    def get_job_status_entry(
        self,
        job_id: str,
    ) -> DatabaseEntry.JobStatus | None:
        cursor = self._db_connection.cursor()
        query = "SELECT * FROM JobStatus WHERE job_id = ?"
        cursor.execute(query, (job_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return DatabaseEntry.JobStatus(
            job_id=row[0],
            init_time=dt.datetime.fromtimestamp(row[1]),
            archived=row[2],
        )

    def set_job_status_entry(
        self,
        job_status_entry: DatabaseEntry.JobStatus,
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        cursor = self._db_connection.cursor()
        columns = ["job_id", "init_time", "archived"]
        values = [
            job_status_entry.job_id,
            job_status_entry.init_time.timestamp(),
            job_status_entry.archived,
        ]
        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO JobStatus ({}) VALUES ({})".format(
                    ", ".join(columns), ", ".join("?" * len(columns))
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE JobStatus SET {} WHERE job_id = ?".format(
                    ", ".join(f"{column} = ?" for column in columns if column != "job_id")
                )
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO JobStatus ({}) VALUES ({}) ON CONFLICT (job_id) DO UPDATE SET {}".format(
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}" for column in columns if column != "job_id"
                    ),
                )
        cursor.execute(query, values)
        self._db_connection.commit()

    # endregion Job Status

    # region   Job Update
    def get_job_update_entry(
        self,
        job_id: str,
        update_time: dt.datetime,
    ) -> DatabaseEntry.JobUpdate | None:
        raise NotImplementedError

    def set_job_update_entry(
        self,
        job_update_entry: DatabaseEntry.JobUpdate,
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        cursor = self._db_connection.cursor()
        columns = ["job_id", "update_time", "new_state", "comment"]
        values = [
            job_update_entry.job_id,
            job_update_entry.update_time.timestamp(),
            job_update_entry.new_state,
            job_update_entry.comment,
        ]
        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO JobUpdate ({}) VALUES ({})".format(
                    ", ".join(columns), ", ".join("?" * len(columns))
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE JobUpdate SET {} WHERE job_id = ?".format(
                    ", ".join(f"{column} = ?" for column in columns if column != "job_id")
                )
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO JobUpdate ({}) VALUES ({}) ON CONFLICT (job_id, update_time) DO UPDATE SET {}".format(
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}"
                        for column in columns
                        if column not in ["job_id", "update_time"]
                    ),
                )

        cursor.execute(query, values)
        self._db_connection.commit()

    # endregion Job Update

    # region   Server Update
    def get_server_update_entry(
        self,
        time: dt.datetime,
    ) -> DatabaseEntry.ServerUpdate | None:
        raise NotImplementedError

    def set_server_update_entry(
        self,
        server_update_entry: DatabaseEntry.ServerUpdate,
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        cursor = self._db_connection.cursor()
        columns = ["update_time", "type", "subtype", "comment"]
        values = [
            int(server_update_entry.update_time.timestamp()),  # TODO: figure out why type is strict
            server_update_entry.type,
            server_update_entry.subtype,
            server_update_entry.comment,
        ]

        if server_update_entry.job_id is not None:
            columns.append("job_id")
            values.append(server_update_entry.job_id)

        if server_update_entry.client_token is not None:
            columns.append("client_token")
            values.append(server_update_entry.client_token)

        match set_method:
            case enums.SQLSetMethod.INSERT:
                query = "INSERT INTO ServerUpdate ({}) VALUES ({})".format(
                    ", ".join(columns), ", ".join("?" * len(columns))
                )
            case enums.SQLSetMethod.UPDATE:
                query = "UPDATE ServerUpdate SET {} WHERE update_time = ?".format(
                    ", ".join(f"{column} = ?" for column in columns if column != "update_time")
                )
            case enums.SQLSetMethod.UPSERT:
                query = "INSERT INTO ServerUpdate ({}) VALUES ({}) ON CONFLICT (update_time) DO UPDATE SET {}".format(
                    ", ".join(columns),
                    ", ".join("?" * len(columns)),
                    ", ".join(
                        f"{column} = EXCLUDED.{column}"
                        for column in columns
                        if column != "update_time"
                    ),
                )

        cursor.execute(query, values)
        self._db_connection.commit()

    # endregion Server Update
    # endregion Public
