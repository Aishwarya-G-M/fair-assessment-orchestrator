from app.adapters.base import (
    BaseFAIRToolAdapter,
    FAIRPrincipleScores,
    FAIRToolResult,
)
from app.schemas.metadata import DatasetMetadata


class MockFairCheckerAdapter(BaseFAIRToolAdapter):
    def assess(self, metadata: DatasetMetadata) -> FAIRToolResult:
        return FAIRToolResult(
            tool_name="fair-checker",
            overall_score=0.64,
            principle_scores=FAIRPrincipleScores(
                findable=0.70,
                accessible=0.68,
                interoperable=0.55,
                reusable=0.63,
            ),
            raw_summary=f"Mock FAIR Checker assessment for {metadata.identifier}",
            notes=[
                "Some metadata fields may be incomplete",
                "Interoperability checks are stricter",
            ],
        )