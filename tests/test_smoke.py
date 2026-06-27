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

    assert "score_difference" in body
    assert "principle_score_difference" in body
    assert "principle_scores" in body["tool_a_result"]
    assert "principle_scores" in body["tool_b_result"]
    assert body["llm_summary"] is None
    assert body["llm_summary_generated"] is False

def test_compare_with_llm_summary() -> None:
    client = TestClient(create_app())

    payload = {
        "metadata": {
            "identifier": "doi:10.1234/example",
            "title": "Example dataset",
            "description": "A sample dataset for FAIR comparison testing"
        },
        "tool_a": "f-uji",
        "tool_b": "fair-checker",
        "include_llm_summary": True
    }

    response = client.post("/compare", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["llm_summary_generated"] is True
    assert body["llm_summary"] is not None