from fastapi.testclient import TestClient


def test_system_endpoints(client: TestClient) -> None:
    health_response = client.get("/healthcheck", headers={"ApiVersion": "1"})
    assert health_response.status_code == 200
    assert health_response.json() == "OK"

    about_response = client.get("/about?show-details=false", headers={"ApiVersion": "1"})
    assert about_response.status_code == 200
    assert about_response.json()["name"] == "PilotApiPython"
