from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    identifier: str = Field(..., description="Dataset identifier, URL, DOI, or other PID")
    title: str
    description: str