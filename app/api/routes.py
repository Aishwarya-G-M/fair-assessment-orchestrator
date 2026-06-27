from fastapi import APIRouter

from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import CompareService

router = APIRouter()
compare_service = CompareService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return compare_service.compare(request)