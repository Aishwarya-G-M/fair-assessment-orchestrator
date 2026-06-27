from app.adapters.base import BaseFAIRToolAdapter
from app.schemas.compare import (
    CompareRequest,
    CompareResponse,
    PrincipleScoreDifference,
    PrincipleScores,
    ToolResult,
)


class CompareService:
    def __init__(self, adapters: dict[str, BaseFAIRToolAdapter]) -> None:
        self.adapters = adapters

    def compare(self, request: CompareRequest) -> CompareResponse:
        adapter_a = self.adapters[request.tool_a]
        adapter_b = self.adapters[request.tool_b]

        result_a = adapter_a.assess(request.metadata)
        result_b = adapter_b.assess(request.metadata)

        score_difference = round(result_a.overall_score - result_b.overall_score, 2)

        principle_difference = PrincipleScoreDifference(
            findable=round(
                result_a.principle_scores.findable
                - result_b.principle_scores.findable,
                2,
            ),
            accessible=round(
                result_a.principle_scores.accessible
                - result_b.principle_scores.accessible,
                2,
            ),
            interoperable=round(
                result_a.principle_scores.interoperable
                - result_b.principle_scores.interoperable,
                2,
            ),
            reusable=round(
                result_a.principle_scores.reusable
                - result_b.principle_scores.reusable,
                2,
            ),
        )

        summary = (
            f"{result_a.tool_name} scored higher overall than {result_b.tool_name}. "
            f"The largest principle-level difference appears in findability and accessibility."
        )

        return CompareResponse(
            tool_a_result=ToolResult(
                tool_name=result_a.tool_name,
                overall_score=result_a.overall_score,
                principle_scores=PrincipleScores(
                    findable=result_a.principle_scores.findable,
                    accessible=result_a.principle_scores.accessible,
                    interoperable=result_a.principle_scores.interoperable,
                    reusable=result_a.principle_scores.reusable,
                ),
                raw_summary=result_a.raw_summary,
                notes=result_a.notes,
            ),
            tool_b_result=ToolResult(
                tool_name=result_b.tool_name,
                overall_score=result_b.overall_score,
                principle_scores=PrincipleScores(
                    findable=result_b.principle_scores.findable,
                    accessible=result_b.principle_scores.accessible,
                    interoperable=result_b.principle_scores.interoperable,
                    reusable=result_b.principle_scores.reusable,
                ),
                raw_summary=result_b.raw_summary,
                notes=result_b.notes,
            ),
            score_difference=score_difference,
            principle_score_difference=principle_difference,
            comparison_summary=summary,
        )