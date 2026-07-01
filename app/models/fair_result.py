from pydantic import BaseModel, Field

from app.schemas.compare import PrincipleScores


class FAIRToolResult(BaseModel):
    tool_name: str
    overall_score: float
    principle_scores: PrincipleScores
    raw_summary: str
    notes: list[str] = Field(default_factory=list)