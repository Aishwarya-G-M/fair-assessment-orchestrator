from app.schemas.compare import CompareResponse
from app.summaries.base import BaseComparisonSummaryProvider


class MockLLMComparisonSummaryProvider(BaseComparisonSummaryProvider):
    def summarize(self, comparison: CompareResponse) -> str:
        tool_a = comparison.tool_a_result
        tool_b = comparison.tool_b_result

        return (
            f"{tool_a.tool_name} performed better overall than {tool_b.tool_name}. "
            f"The strongest differences appear in findability and accessibility. "
            f"This summary is mock-generated from normalized comparison data."
        )