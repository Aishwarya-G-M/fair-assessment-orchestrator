from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_compare() -> None:
    client = TestClient(create_app())

    payload = {
        "metadata": {
            "identifier": "doi:10.1234/example",
            "title": "Example dataset",
            "description": "A sample dataset for FAIR comparison testing"
        },
        "tool_a": "f-uji",
        "tool_b": "fair-checker"
    }

    response = client.post("/compare", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert "tool_a_result" in body
    assert "tool_b_result" in body
    assert "comparison_summary" in body