from app.llm.base import BaseLLMClient
from app.schemas.compare import CompareResponse
from app.summaries.base import BaseComparisonSummaryProvider


class LLMComparisonSummaryProvider(BaseComparisonSummaryProvider):
    def __init__(self, llm_client: BaseLLMClient) -> None:
        self.llm_client = llm_client

    def summarize(self, comparison: CompareResponse) -> str:
        prompt = self._build_prompt(comparison)
        return self.llm_client.generate(prompt)

    def _build_prompt(self, comparison: CompareResponse) -> str:
        return (
            "Summarize the FAIR assessment comparison in plain language.\n\n"
            f"Tool A: {comparison.tool_a_result.tool_name}\n"
            f"Tool A overall score: {comparison.tool_a_result.overall_score}\n"
            f"Tool A findable: {comparison.tool_a_result.principle_scores.findable}\n"
            f"Tool A accessible: {comparison.tool_a_result.principle_scores.accessible}\n"
            f"Tool A interoperable: {comparison.tool_a_result.principle_scores.interoperable}\n"
            f"Tool A reusable: {comparison.tool_a_result.principle_scores.reusable}\n\n"
            f"Tool B: {comparison.tool_b_result.tool_name}\n"
            f"Tool B overall score: {comparison.tool_b_result.overall_score}\n"
            f"Tool B findable: {comparison.tool_b_result.principle_scores.findable}\n"
            f"Tool B accessible: {comparison.tool_b_result.principle_scores.accessible}\n"
            f"Tool B interoperable: {comparison.tool_b_result.principle_scores.interoperable}\n"
            f"Tool B reusable: {comparison.tool_b_result.principle_scores.reusable}\n\n"
            f"Overall score difference: {comparison.score_difference}\n"
            f"Findable difference: {comparison.principle_score_difference.findable}\n"
            f"Accessible difference: {comparison.principle_score_difference.accessible}\n"
            f"Interoperable difference: {comparison.principle_score_difference.interoperable}\n"
            f"Reusable difference: {comparison.principle_score_difference.reusable}\n\n"
            "Be concise and avoid inventing facts."
        )