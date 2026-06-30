from fastapi import APIRouter

from app.adapters.fuji_adapter import FUJIAdapter
from app.adapters.mock_fair_checker import MockFairCheckerAdapter
from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import CompareService
from app.summaries.base import BaseComparisonSummaryProvider
from app.summaries.llm_summary import LLMComparisonSummaryProvider

router = APIRouter()


def get_summary_provider() -> BaseComparisonSummaryProvider | None:
    try:
        from app.llm.groq_client import GroqLLMClient
    except ModuleNotFoundError:
        return None

    return LLMComparisonSummaryProvider(
        llm_client=GroqLLMClient(),
    )


compare_service = CompareService(
    adapters={
        "f-uji": FUJIAdapter(),
        "fair-checker": MockFairCheckerAdapter(),
    },
    summary_provider=get_summary_provider(),
)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return compare_service.compare(request)