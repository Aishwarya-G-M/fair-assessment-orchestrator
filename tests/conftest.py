import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.compare_service import CompareService
from dependencies import get_compare_service
from tests.mocks.adapters import MockFUJIAdapter, MockFairCheckerAdapter


@pytest.fixture
def test_compare_service():
    return CompareService(
        adapters={
            "f-uji": MockFUJIAdapter(),
            "fair-checker": MockFairCheckerAdapter(),
        },
        summary_provider=None,
    )


@pytest.fixture
def client(test_compare_service):
    app.dependency_overrides[get_compare_service] = lambda: test_compare_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()