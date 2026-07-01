from app.adapters.fuji_adapter import FUJIAdapter
from app.services.compare_service import CompareService
from app.adapters.fair_checker import FAIRCheckerAdapter

def get_compare_service() -> CompareService:
    return CompareService(
        adapters={
            "f-uji": FUJIAdapter(),
            "fair-checker": FAIRCheckerAdapter(),
        },
        summary_provider=None,
    )