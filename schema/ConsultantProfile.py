from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from model.ConsultantEnum import ConsultantEnum
import logging
logger = logging.getLogger(__name__)


class ConsultantProfileSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the consultant")
    email: str
    skills: List[str] = Field(..., description="Skills of the consultant stored as a JSON array")
    experience: Optional[int] = Field(None, ge=0, description="Years of experience of the consultant")
    location: Optional[str] = Field(None, max_length=100, description="Location of the consultant")
    project: Optional[str] = Field(None, min_length=10, description="Past Project details")
    availability: ConsultantEnum = Field(default=ConsultantEnum.available,
                                         description="Availability status of the consultant")

    class Config:
        from_attributes = True

class ConsultantProfileOutput(ConsultantProfileSchema):
    id: int
