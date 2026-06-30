import pytest
from fastapi.testclient import TestClient

from app.api.routes import compare_service
from app.main import create_app
from app.schemas.compare import PrincipleScores, ToolResult


class FakeFUJIAdapter:
    def assess(self, metadata):
        return ToolResult(
            tool_name="f-uji",
            overall_score=0.78,
            principle_scores=PrincipleScores(
                findable=0.80,
                accessible=0.75,
                interoperable=0.70,
                reusable=0.85,
            ),
            raw_summary=f"F-UJI assessed {metadata.identifier}",
            notes=["FsF-F1-01D: Persistent identifier: pass"],
        )


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_fuji_adapter():
    original = compare_service.adapters["f-uji"]
    compare_service.adapters["f-uji"] = FakeFUJIAdapter()
    yield
    compare_service.adapters["f-uji"] = original

def test_compare(client, fake_fuji_adapter):
    response = client.post(
        "/compare",
        json={
            "metadata": {
                "identifier": "doi:10.1234/example",
                "title": "Example dataset",
                "description": "A sample dataset",
            },
            "tool_a": "f-uji",
            "tool_b": "fair-checker",
        },
    )

    assert response.status_code == 200