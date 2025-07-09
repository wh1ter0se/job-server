import pytest
import jobserver as jserv
from fastapi.testclient import TestClient
from tests.fixtures.clients import (
    temporary_directory,
    config_client,
    database_client,
)
from tests.fixtures.jobs.file_write_read_job import (
    FileWriteReadJob,
    file_write_read_job_server,
    file_write_read_job_client,
)


class TestJobManagerBasicFunctionality:
    @pytest.mark.dependency(name="test_job_manager_can_start")
    def test_job_manager_can_start(
        self,
        config_client: jserv.ConfigClient,
        database_client: jserv.DatabaseClient,
    ):
        job_manager = jserv.JobManager(
            config=config_client,
            database=database_client,
        )
        job_manager.start()

    def test_job_manager_returns_job_template(
        self,
        config_client: jserv.ConfigClient,
        database_client: jserv.DatabaseClient,
    ):
        job_manager = jserv.JobManager(
            config=config_client,
            database=database_client,
        )


class TestJobServerBasicFunctionality:
    @pytest.mark.dependency(
        name="test_server_can_start",
        depends=["test_job_manager_can_start"],
    )
    def test_server_can_start(self, file_write_read_job_server: jserv.JobServer):
        file_write_read_job_server.start()
        assert file_write_read_job_server._app is not None

    @pytest.mark.dependency(
        name="test_server_get",
        depends=["test_server_can_start"],
    )
    def test_server_get(self, file_write_read_job_client: TestClient):
        response = file_write_read_job_client.get("/")
        assert response.status_code == 200
        assert response.json() == {}

    @pytest.mark.dependency(
        name="test_server_post",
        depends=["test_server_can_start"],
    )
    def test_server_post(self, file_write_read_job_client: TestClient):
        response = file_write_read_job_client.post("/")
        assert response.status_code == 200


@pytest.mark.xfail(raises=NotImplementedError)
@pytest.mark.dependency(depends=["test_server_get", "test_server_post"])
class TestJobServerEndpoints:
    def test_endpoint_connection(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/connection/NOT_REAL_TOKEN")
        assert response.status_code == 200

    def test_endpoint_connections(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/connections/")
        assert response.status_code == 200

    def test_endpoint_error(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/error/NOT_REAL_ERROR_ID")
        assert response.status_code == 200

    def test_endpoint_errors(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/errors/")
        assert response.status_code == 200

    def test_endpoint_job_template(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/job_template/NOT_REAL_NAME")
        assert response.status_code == 200

    def test_endpoint_job_templates(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/job_templates/")
        assert response.status_code == 200

    def test_endpoint_status(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/status/")
        assert response.status_code == 200

    def test_endpoint_server_updates(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/server_updates/")
        assert response.status_code == 200

    def test_endpoint_active_jobs(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/active_jobs/")
        assert response.status_code == 200

    def test_endpoint_job_updates(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/job_updates")
        assert response.status_code == 200

    def test_endpoint_job_status(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/job/status/NOT_REAL_JOB_ID")
        assert response.status_code == 200

    def test_endpoint_job_submit(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.post("/job/submit/NOT_REAL_JOB_ID", json={})
        assert response.status_code == 200

    def test_endpoint_job_start(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.post("/job/start/NOT_REAL_JOB_ID")
        assert response.status_code == 200

    def test_endpoint_job_pause(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.post("/job/pause/NOT_REAL_JOB_ID")
        assert response.status_code == 200

    def test_endpoint_job_resume(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.post("/job/resume/NOT_REAL_JOB_ID")
        assert response.status_code == 200

    def test_endpoint_job_cancel(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.post("/job/cancel/NOT_REAL_JOB_ID")
        assert response.status_code == 200

    def test_endpoint_job_subscribe(self, file_write_read_job_client: TestClient) -> None:
        response = file_write_read_job_client.get("/job/subscribe/NOT_REAL_JOB_ID")
        assert response.status_code == 200
