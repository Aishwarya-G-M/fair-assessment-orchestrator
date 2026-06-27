from fastapi import APIRouter

from app.adapters.mock_fair_checker import MockFairCheckerAdapter
from app.adapters.mock_fuji import MockFujiAdapter
from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import CompareService

router = APIRouter()

compare_service = CompareService(
    adapters={
        "f-uji": MockFujiAdapter(),
        "fair-checker": MockFairCheckerAdapter(),
    }
)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return compare_service.compare(request)