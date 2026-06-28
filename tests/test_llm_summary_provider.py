from app.llm.mock_client import MockLLMClient
from app.schemas.compare import (
    CompareResponse,
    PrincipleScoreDifference,
    PrincipleScores,
    ToolResult,
)
from app.summaries.llm_summary import LLMComparisonSummaryProvider


def test_llm_summary_provider_returns_generated_text() -> None:
    provider = LLMComparisonSummaryProvider(llm_client=MockLLMClient())

    comparison = CompareResponse(
        tool_a_result=ToolResult(
            tool_name="f-uji",
            overall_score=0.72,
            principle_scores=PrincipleScores(
                findable=0.80,
                accessible=0.75,
                interoperable=0.60,
                reusable=0.73,
            ),
            raw_summary="Mock A",
            notes=[],
        ),
        tool_b_result=ToolResult(
            tool_name="fair-checker",
            overall_score=0.64,
            principle_scores=PrincipleScores(
                findable=0.70,
                accessible=0.68,
                interoperable=0.55,
                reusable=0.63,
            ),
            raw_summary="Mock B",
            notes=[],
        ),
        score_difference=0.08,
        principle_score_difference=PrincipleScoreDifference(
            findable=0.10,
            accessible=0.07,
            interoperable=0.05,
            reusable=0.10,
        ),
        comparison_summary="Structured comparison",
        llm_summary=None,
        llm_summary_generated=False,
    )

    summary = provider.summarize(comparison)

    assert summary is not None
    assert "Mock LLM summary" in summary