from pydantic import BaseModel, Field

from app.schemas.metadata import DatasetMetadata


class CompareRequest(BaseModel):
    metadata: DatasetMetadata
    tool_a: str = Field(..., description="Primary FAIR assessment tool")
    tool_b: str = Field(..., description="Secondary FAIR assessment tool")


class ToolResult(BaseModel):
    tool_name: str
    overall_score: float
    raw_summary: str


class CompareResponse(BaseModel):
    tool_a_result: ToolResult
    tool_b_result: ToolResult
    comparison_summary: str