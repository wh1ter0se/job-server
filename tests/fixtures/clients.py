import os
import pytest
import shutil
import datetime as dt
import jobserver as jserv
from pathlib import Path
from typing import Generator


@pytest.fixture()
def temporary_directory() -> Generator[Path, None, None]:
    tmp_time = dt.datetime.now()
    tmp_dir = Path(f".tmp/{tmp_time.timestamp()}/")
    os.makedirs(tmp_dir, exist_ok=True)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


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
