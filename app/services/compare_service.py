from app.schemas.compare import CompareRequest, CompareResponse, ToolResult


class CompareService:
    def compare(self, request: CompareRequest) -> CompareResponse:
        tool_a_result = ToolResult(
            tool_name=request.tool_a,
            overall_score=0.72,
            raw_summary="Stub result from tool A"
        )
        tool_b_result = ToolResult(
            tool_name=request.tool_b,
            overall_score=0.64,
            raw_summary="Stub result from tool B"
        )

        summary = (
            f"{request.tool_a} returned a higher score than {request.tool_b}. "
            f"This is a placeholder comparison summary."
        )

        return CompareResponse(
            tool_a_result=tool_a_result,
            tool_b_result=tool_b_result,
            comparison_summary=summary,
        )