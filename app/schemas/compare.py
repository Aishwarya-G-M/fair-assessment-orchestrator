from typing import Any

from pydantic import BaseModel, Field

from app.schemas.metadata import DatasetMetadata


class CompareRequest(BaseModel):
    metadata: DatasetMetadata
    tool_a: str = Field(..., description="Primary FAIR assessment tool")
    tool_b: str = Field(..., description="Secondary FAIR assessment tool")
    include_llm_summary: bool = Field(
        default=False,
        description="Whether to include an LLM-generated comparison summary",
    )


class PrincipleScores(BaseModel):
    findable: float | None = None
    accessible: float | None = None
    interoperable: float | None = None
    reusable: float | None = None


class ToolResult(BaseModel):
    tool_name: str
    overall_score: float | None = None
    principle_scores: PrincipleScores | None = None
    raw_summary: str | None = None
    notes: list[str] = Field(default_factory=list)

    raw_payload: dict[str, Any] | list[Any] | str | None = None
    llm_context: str | None = None
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None


class PrincipleScoreDifference(BaseModel):
    findable: float | None = None
    accessible: float | None = None
    interoperable: float | None = None
    reusable: float | None = None


class CompareResponse(BaseModel):
    tool_a_result: ToolResult
    tool_b_result: ToolResult
    score_difference: float | None = None
    principle_score_difference: PrincipleScoreDifference
    comparison_summary: str
    llm_summary: str | None = None
    llm_summary_generated: bool = False