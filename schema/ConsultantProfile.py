from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from model.ConsultantEnum import ConsultantEnum


class ConsultantProfileSchema(BaseModel):
    id: str = Field(..., description="UUID of the consultant profile")
    name: str = Field(..., min_length=1, max_length=255, description="Name of the consultant")
    email: str
    skills: List[str] = Field(..., description="Skills of the consultant stored as a JSON array")
    experience: Optional[int] = Field(None, ge=0, description="Years of experience of the consultant")
    location: Optional[str] = Field(None, max_length=100, description="Location of the consultant")
    availability: ConsultantEnum = Field(default=ConsultantEnum.available, description="Availability status of the consultant")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Config:
        from_attributes = True