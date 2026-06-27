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
    findable: float
    accessible: float
    interoperable: float
    reusable: float


class ToolResult(BaseModel):
    tool_name: str
    overall_score: float
    principle_scores: PrincipleScores
    raw_summary: str
    notes: list[str] = Field(default_factory=list)


class PrincipleScoreDifference(BaseModel):
    findable: float
    accessible: float
    interoperable: float
    reusable: float


class CompareResponse(BaseModel):
    tool_a_result: ToolResult
    tool_b_result: ToolResult
    score_difference: float
    principle_score_difference: PrincipleScoreDifference
    comparison_summary: str
    llm_summary: str | None = None
    llm_summary_generated: bool = False