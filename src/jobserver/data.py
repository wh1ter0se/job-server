import os
import json
import shutil
import sqlite3
import datetime as dt
import importlib.resources
from pathlib import Path
from typing import Any
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


class DatabaseEntry:

    class Connection:
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

    class Error:
        error_id: str  # Primary key
        error_time: dt.datetime
        severity_level: enums.ErrorSeverity
        traceback: str
        job_hash: str | None  # FK
        client_token: str | None  # FK

        def __init__(
            self,
            error_id: str,
            error_time: dt.datetime,
            severity_level: enums.ErrorSeverity,
            traceback: str,
            job_hash: str | None,
            client_token: str | None,
        ) -> None:
            self.error_id = error_id
            self.error_time = error_time
            self.severity_level = severity_level
            self.traceback = traceback
            self.job_hash = job_hash
            self.client_token = client_token

        def __eq__(self, value) -> bool:
            return (
                self.error_id == value.error_id
                and self.error_time == value.error_time
                and self.severity_level == value.severity_level
                and self.traceback == value.traceback
                and self.job_hash == value.job_hash
                and self.client_token == value.client_token
            )

    class JobStatus:
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

        def __eq__(self, value) -> bool:
            return self.job_id == value.job_id and self.init_time == value.init_time

    class JobUpdate:
        job_id: str  # Primary key
        update_time: dt.datetime  # Primary key
        new_state: int
        comment: str

        def __init__(
            self,
            job_id: str,
            update_time: dt.datetime,
            new_state: int,
            comment: str,
        ) -> None:
            self.job_id = job_id
            self.update_time = update_time
            self.new_state = new_state
            self.comment = comment

        def __eq__(self, value) -> bool:
            return (
                self.job_id == value.job_id
                and self.update_time == value.update_time
                and self.new_state == value.new_state
                and self.comment == value.comment
            )

    class ServerUpdate:
        time: dt.datetime  # Primary key
        type: int
        subtype: int
        job_id: str | None  # FK

        def __init__(
            self,
            time: dt.datetime,
            type: int,
            subtype: int,
            job_id: str | None,
        ) -> None:
            self.time = time
            self.type = type
            self.subtype = subtype
            self.job_id = job_id

        def __eq__(self, value) -> bool:
            return (
                self.time == value.time
                and self.type == value.type
                and self.subtype == value.subtype
                and self.job_id == value.job_id
            )


class DatabaseClient:

    config: ConfigClient
    _connection: sqlite3.Connection

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
            self._connection = sqlite3.connect(db_file_path)
            print(f"Connected to database: {db_file_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise e

    def disconnect(self) -> None:
        self._connection.close()

    # endregion Private

    # region Public
    # region  Table Getters/Setters
    # region   Connection
    def get_connection_entry(
        self,
        client_token: str,
    ) -> DatabaseEntry.Connection | None:
        cursor = self._connection.cursor()
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

    def get_connection_entries(
        self,
        before: dt.datetime | None = None,
        after: dt.datetime | None = None,
        limit: int = 0,
        offset: int = 0,
    ) -> list[DatabaseEntry.Connection] | None:
        cursor = self._connection.cursor()
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
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        cursor = self._connection.cursor()
        match set_method:
            case enums.SQLSetMethod.INSERT:
                if connection_entry.last_message_time is None:
                    # If last_message_time is None, we don't include it in the insert statement
                    cursor.execute(
                        """
                        INSERT INTO Connection (client_token, init_time, num_messages, client_ip)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            connection_entry.client_token,
                            connection_entry.init_time.timestamp(),
                            connection_entry.num_messages,
                            connection_entry.client_ip,
                        ),
                    )
                else:
                    # If last_message_time is provided, we include it in the insert statement
                    cursor.execute(
                        f"""
                        INSERT INTO Connection (client_token, init_time, last_message_time, num_messages, client_ip)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            connection_entry.client_token,
                            connection_entry.init_time.timestamp(),
                            connection_entry.last_message_time.timestamp(),
                            connection_entry.num_messages,
                            connection_entry.client_ip,
                        ),
                    )
            case enums.SQLSetMethod.UPDATE:
                cursor.execute(
                    f"""
                    UPDATE Connection
                    SET init_time = ?, last_message_time = ?, num_messages = ?, client_ip = ?
                    WHERE client_token = ?
                    """,
                    (
                        connection_entry.init_time.timestamp(),
                        (
                            connection_entry.last_message_time.timestamp()
                            if connection_entry.last_message_time is not None
                            else None
                        ),
                        connection_entry.num_messages,
                        connection_entry.client_ip,
                        connection_entry.client_token,
                    ),
                )
            case enums.SQLSetMethod.UPSERT:
                raise NotImplementedError
        self._connection.commit()

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
        raise NotImplementedError

    # endregion Error

    # region   Job Status
    def get_job_status_entry(
        self,
        job_hash: str,
    ) -> DatabaseEntry.JobStatus | None:
        raise NotImplementedError

    # endregion Job Status

    # region   Job Update
    def get_job_update_entry(
        self,
        job_id: str,
        update_time: dt.datetime,
    ) -> DatabaseEntry.JobUpdate | None:
        raise NotImplementedError

    # endregion Job Update

    # region   Server Update
    def get_server_update_entry(
        self,
        time: dt.datetime,
    ) -> DatabaseEntry.ServerUpdate | None:
        raise NotImplementedError

    # endregion Server Update
    # endregion Table Getters/Setters
    # endregion Public
