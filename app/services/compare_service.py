from app.adapters.base import BaseFAIRToolAdapter
from app.schemas.compare import (
    CompareRequest,
    CompareResponse,
    PrincipleScoreDifference,
)
from app.summaries.base import BaseComparisonSummaryProvider


class CompareService:
    def __init__(
        self,
        adapters: dict[str, BaseFAIRToolAdapter],
        summary_provider: BaseComparisonSummaryProvider | None = None,
    ) -> None:
        self.adapters = adapters
        self.summary_provider = summary_provider

    def compare(self, request: CompareRequest) -> CompareResponse:
        adapter_a = self.adapters[request.tool_a]
        adapter_b = self.adapters[request.tool_b]

        result_a = adapter_a.assess(request.metadata)
        result_b = adapter_b.assess(request.metadata)

        score_difference = self._diff(result_a.overall_score, result_b.overall_score)

        principle_difference = PrincipleScoreDifference(
            findable=self._diff(
                self._principle_value(result_a, "findable"),
                self._principle_value(result_b, "findable"),
            ),
            accessible=self._diff(
                self._principle_value(result_a, "accessible"),
                self._principle_value(result_b, "accessible"),
            ),
            interoperable=self._diff(
                self._principle_value(result_a, "interoperable"),
                self._principle_value(result_b, "interoperable"),
            ),
            reusable=self._diff(
                self._principle_value(result_a, "reusable"),
                self._principle_value(result_b, "reusable"),
            ),
        )

        comparison = CompareResponse(
            tool_a_result=result_a,
            tool_b_result=result_b,
            score_difference=score_difference,
            principle_score_difference=principle_difference,
            comparison_summary=self._build_comparison_summary(result_a, result_b),
        )

        if request.include_llm_summary and self.summary_provider is not None:
            comparison.llm_summary = self.summary_provider.summarize(comparison)
            comparison.llm_summary_generated = True

        return comparison

    def _diff(self, a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return round(a - b, 2)

    def _principle_value(self, result, principle: str) -> float | None:
        if result.principle_scores is None:
            return None
        return getattr(result.principle_scores, principle, None)

    def _build_comparison_summary(self, result_a, result_b) -> str:
        if result_a.error and result_b.error:
            return (
                f"Both {result_a.tool_name} and {result_b.tool_name} returned errors."
            )

        if result_a.error:
            return f"{result_a.tool_name} returned an error; {result_b.tool_name} completed."
        if result_b.error:
            return f"{result_b.tool_name} returned an error; {result_a.tool_name} completed."

        if result_a.overall_score is not None and result_b.overall_score is not None:
            if result_a.overall_score > result_b.overall_score:
                return (
                    f"{result_a.tool_name} scored higher overall than "
                    f"{result_b.tool_name}."
                )
            if result_b.overall_score > result_a.overall_score:
                return (
                    f"{result_b.tool_name} scored higher overall than "
                    f"{result_a.tool_name}."
                )
            return f"{result_a.tool_name} and {result_b.tool_name} scored equally overall."

        return (
            f"Completed comparison between {result_a.tool_name} and "
            f"{result_b.tool_name}, but at least one tool did not provide a normalized overall score."
        )