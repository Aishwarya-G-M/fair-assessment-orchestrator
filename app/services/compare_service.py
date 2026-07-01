from __future__ import annotations

from typing import Any

from app.schemas.compare import (
    CompareRequest,
    CompareResponse,
    PrincipleScoreDifference,
    ToolResult,
)


class CompareService:
    def __init__(self, adapters: dict[str, Any], summary_provider: Any = None):
        self.adapters = adapters
        self.summary_provider = summary_provider

    def compare(self, request: CompareRequest) -> CompareResponse:
        if request.tool_a not in self.adapters:
            raise ValueError(f"Unsupported tool: {request.tool_a}")
        if request.tool_b not in self.adapters:
            raise ValueError(f"Unsupported tool: {request.tool_b}")

        tool_a_adapter = self.adapters[request.tool_a]
        tool_b_adapter = self.adapters[request.tool_b]

        tool_a_result: ToolResult = tool_a_adapter.assess(request.metadata)
        tool_b_result: ToolResult = tool_b_adapter.assess(request.metadata)

        score_difference = self._diff(
            tool_a_result.overall_score,
            tool_b_result.overall_score,
        )

        principle_score_difference = PrincipleScoreDifference(
            findable=self._diff(
                self._principle(tool_a_result, "findable"),
                self._principle(tool_b_result, "findable"),
            ),
            accessible=self._diff(
                self._principle(tool_a_result, "accessible"),
                self._principle(tool_b_result, "accessible"),
            ),
            interoperable=self._diff(
                self._principle(tool_a_result, "interoperable"),
                self._principle(tool_b_result, "interoperable"),
            ),
            reusable=self._diff(
                self._principle(tool_a_result, "reusable"),
                self._principle(tool_b_result, "reusable"),
            ),
        )

        comparison_summary = self._build_summary(
            request.tool_a,
            request.tool_b,
            tool_a_result.overall_score,
            tool_b_result.overall_score,
        )

        response = CompareResponse(
            tool_a_result=tool_a_result,
            tool_b_result=tool_b_result,
            score_difference=score_difference,
            principle_score_difference=principle_score_difference,
            comparison_summary=comparison_summary,
            llm_summary=None,
            llm_summary_generated=False,
        )

        if request.include_llm_summary and self.summary_provider:
            llm_summary = self.summary_provider.summarize(response)
            response.llm_summary = llm_summary
            response.llm_summary_generated = llm_summary is not None

        return response

    @staticmethod
    def _principle(result: ToolResult, field: str) -> float | None:
        if result.principle_scores is None:
            return None
        return getattr(result.principle_scores, field, None)

    @staticmethod
    def _diff(a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return round(a - b, 2)

    @staticmethod
    def _build_summary(
        tool_a: str,
        tool_b: str,
        score_a: float | None,
        score_b: float | None,
    ) -> str:
        if score_a is None or score_b is None:
            return (
                f"Comparison completed for {tool_a} and {tool_b}, "
                "but one or both overall scores were unavailable."
            )

        if score_a > score_b:
            return f"{tool_a} scored higher overall than {tool_b}."
        if score_b > score_a:
            return f"{tool_b} scored higher overall than {tool_a}."
        return f"{tool_a} and {tool_b} scored equally overall."