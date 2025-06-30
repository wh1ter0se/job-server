import os
import time
import shutil
import pytest
import datetime as dt
import jobserver as jserv
from typing import Generator
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


def test_database_client_can_load(config_client: jserv.ConfigClient) -> None:
    database = jserv.DatabaseClient(config=config_client)
    assert database


@pytest.fixture()
def database_client(config_client: jserv.ConfigClient) -> jserv.DatabaseClient:
    database = jserv.DatabaseClient(config=config_client)
    return database


# def test_config_set_get_connection(database_client: jserv.DatabaseClient):
#     client_token = "test_token"
#     init_time = dt.datetime.now()
#     last_message_time = None
#     num_messages = 0

#     database_client.set_connection_entry(
#         client_token=client_token,
#         init_time=init_time,
#         last_message_time=last_message_time,
#         num_messages=num_messages,
#         set_method=jserv.enums.SQLSetMethod.INSERT,
#     )

#     connection_entry = database_client.get_connection_entry(client_token="test_token")
#     assert connection_entry is not None
#     assert connection_entry.client_token == client_token
#     assert connection_entry.init_time == init_time
#     assert connection_entry.last_message_time == last_message_time
#     assert connection_entry.num_messages == num_messages
