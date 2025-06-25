import json
import sqlite3
from pathlib import Path
from typing import Callable, Any
from src.enums import ConfigValue


class ConfigClient:

    _config: dict

    def __init__(
        self,
        config_file: Path = Path("/assets/default_config.json"),
    ):
        self.config_file = config_file
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from the specified JSON file."""
        try:
            with open(self.config_file, "r") as file:
                self._config = json.load(file)
        except Exception as e:
            print(f"Error loading config file {self.config_file}: {e}")
            raise e

    def _save_config(self) -> None:
        """Save the current configuration to the specified JSON file."""
        try:
            with open(self.config_file, "w") as file:
                json.dump(self._config, file, indent=4)
        except Exception as e:
            print(f"Error saving config file {self.config_file}: {e}")
            raise e

    def get(self, key: str) -> Any:
        """Get a value from the configuration."""
        return self._config.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set a value in the configuration."""
        self._config[key] = value
        self._save_config()


class DatabaseClient:

    config: ConfigClient

    def __init__(self, config: ConfigClient):
        self.config = config

    def _get_connection(self, db_file: Path) -> sqlite3.Connection:
        """Create a database connection to the SQLite database specified by db_file."""
        try:
            connection = sqlite3.connect(
                self.config.get(
                    key=ConfigValue.DATABASE_PATH.value,
                )
            )
            print(f"Connected to database: {db_file}")
            return connection
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise e

    # def get_job_status(job_hash: str) -> None:
    #     # Open database/jobserver.sqlite3
    #     db_file = Path()
