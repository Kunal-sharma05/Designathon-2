from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchResultSchema(BaseModel):
    job_description_id: str = Field(..., description="Foreign key to the job description ID")
    consultant_id: str = Field(..., description="Foreign key to the consultant profile ID")
    similarity_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Similarity score between 0.0 and 1.0"
    )
    rank: int = Field(..., ge=1, description="Rank of the match result (must be a positive integer)")
    matched_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the match was created")

    class Config:
        from_attributes = True


class MatchResultSchemaCreate(MatchResultSchema):
    pass
