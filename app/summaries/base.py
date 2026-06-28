from abc import ABC, abstractmethod

from app.schemas.compare import CompareResponse


class BaseComparisonSummaryProvider(ABC):
    @abstractmethod
    def summarize(self, comparison: CompareResponse) -> str:
        pass