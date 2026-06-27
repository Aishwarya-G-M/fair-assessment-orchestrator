from fastapi import APIRouter

from app.adapters.mock_fair_checker import MockFairCheckerAdapter
from app.adapters.mock_fuji import MockFujiAdapter
from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import CompareService
from app.summaries.mock_llm_summary import MockLLMComparisonSummaryProvider

router = APIRouter()

compare_service = CompareService(
    adapters={
        "f-uji": MockFujiAdapter(),
        "fair-checker": MockFairCheckerAdapter(),
    },
    summary_provider=MockLLMComparisonSummaryProvider(),
)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return compare_service.compare(request)