from abc import ABC, abstractmethod

from app.schemas.compare import ToolResult
from app.schemas.metadata import DatasetMetadata


class FAIRPrincipleScores:
    def __init__(
        self,
        findable: float,
        accessible: float,
        interoperable: float,
        reusable: float,
    ) -> None:
        self.findable = findable
        self.accessible = accessible
        self.interoperable = interoperable
        self.reusable = reusable


class FAIRToolResult:
    def __init__(
        self,
        tool_name: str,
        overall_score: float,
        principle_scores: FAIRPrincipleScores,
        raw_summary: str,
        notes: list[str] | None = None,
    ) -> None:
        self.tool_name = tool_name
        self.overall_score = overall_score
        self.principle_scores = principle_scores
        self.raw_summary = raw_summary
        self.notes = notes or []


class BaseFAIRToolAdapter(ABC):
    @abstractmethod
    def assess(self, metadata: DatasetMetadata) -> ToolResult:
        pass