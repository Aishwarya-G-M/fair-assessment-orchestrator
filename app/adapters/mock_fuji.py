from app.adapters.base import (
    BaseFAIRToolAdapter,
    FAIRPrincipleScores,
    FAIRToolResult,
)
from app.schemas.metadata import DatasetMetadata


class MockFujiAdapter(BaseFAIRToolAdapter):
    def assess(self, metadata: DatasetMetadata) -> FAIRToolResult:
        return FAIRToolResult(
            tool_name="f-uji",
            overall_score=0.72,
            principle_scores=FAIRPrincipleScores(
                findable=0.80,
                accessible=0.75,
                interoperable=0.60,
                reusable=0.73,
            ),
            raw_summary=f"Mock F-UJI assessment for {metadata.identifier}",
            notes=[
                "PID detected",
                "Metadata quality appears moderate",
            ],
        )