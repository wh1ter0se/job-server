import pytest
import jobserver as jserv
from fastapi.testclient import TestClient
from tests.fixtures.jobs.file_write_read_job import (
    FileWriteReadJob,
    file_write_read_job_server,
    file_write_read_job_client,
)


# def test_server_can_start(file_write_read_job_server: jserv.JobServer):
#     file_write_read_job_server.start()
#     assert file_write_read_job_server._app is not None


# def test_endpoint_server_status(file_write_read_job_client: TestClient):
#     response = file_write_read_job_client.get("/get_server_status/")
#     assert response.status_code == 200
#     assert "init_time" in dict(response.json()).keys()


# @pytest.mark.xfail(raises=NotImplementedError)
# def test_endpoint_connections(file_write_read_job_client: TestClient):
#     response = file_write_read_job_client.get("/get_connections/")
#     assert response.status_code == 200
#     # TODO check contents of the response


# @pytest.mark.xfail(raises=NotImplementedError)
# def test_endpoint_errors(file_write_read_job_client: TestClient):
#     response = file_write_read_job_client.get("/get_errors/")
#     assert response.status_code == 200
#     # TODO check contents of the response


# @pytest.mark.xfail(raises=NotImplementedError)
# def test_client_returns_active_jobs(file_write_read_job_client: TestClient):
#     response = file_write_read_job_client.get("/get_active_jobs/")
#     assert response.status_code == 200
#     # TODO check contents of the response


# @pytest.mark.xfail(raises=NotImplementedError)
# def test_client_returns_job_templates(file_write_read_job_client: TestClient):
#     response = file_write_read_job_client.get("/get_job_templates/")
#     assert response.status_code == 200
#     # TODO check contents of the response
