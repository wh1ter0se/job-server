import os
import json
import sqlite3
import datetime as dt
from pathlib import Path
from typing import Any
from . import enums


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
        # TODO: figure out how to unload default config from python package assets
        raise NotImplementedError

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

    class Error:
        error_id: str  # Primary key
        error_time: dt.datetime
        severity_level: enums.ErrorSeverity
        traceback: str
        job_hash: str | None  # FK
        client_token: str | None  # FK

    class JobStatus:
        job_id: str  # Primary key
        init_time: dt.datetime
        archived: bool

    class JobUpdate:
        job_id: str  # Primary key
        update_time: dt.datetime  # Primary key
        new_state: int
        comment: str

    class ServerUpdate:
        time: dt.datetime  # Primary key
        type: int
        subtype: int
        job_id: str | None  # FK


class DatabaseClient:

    config: ConfigClient

    def __init__(self, config: ConfigClient):
        self.config = config

    # region Private
    def _connect(self, db_file: Path) -> sqlite3.Connection:
        """Create a database connection to the SQLite database specified by db_file."""
        try:
            _db_path: str = self.config.get(key=enums.ConfigValue.DATABASE_PATH.value)
            db_path = Path(_db_path)
            if not db_path.exists():
                raise FileNotFoundError(f"Database file not found: {db_path}")
            connection = sqlite3.connect(db_path)
            print(f"Connected to database: {db_file}")
            return connection
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise e

    # endregion Private

    # region Public
    # region  Table Getters/Setters
    # region   Connection
    def get_connection_entry(
        self,
        client_token: str,
    ) -> DatabaseEntry.Connection | None:
        raise NotImplementedError

    def set_connection_entry(
        self,
        client_token: str,
        init_time: dt.datetime,
        last_message_time: dt.datetime | None,
        num_messages: int,
        set_method=enums.SQLSetMethod.INSERT,
    ) -> None:
        # Build struct
        connection_entry = DatabaseEntry.Connection()
        connection_entry.client_token = client_token
        connection_entry.init_time = init_time
        connection_entry.last_message_time = last_message_time
        connection_entry.num_messages = num_messages

        match set_method:
            case enums.SQLSetMethod.INSERT:
                raise NotImplementedError
            case enums.SQLSetMethod.UPDATE:
                raise NotImplementedError
            case enums.SQLSetMethod.UPSERT:
                raise NotImplementedError

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
