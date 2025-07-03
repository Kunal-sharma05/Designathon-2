from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from model.JobDescriptionEnum import JobDescriptionEnum
import logging

logger = logging.getLogger(__name__)


class JobDescriptionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the job description")
    department: Optional[str] = Field(None, max_length=100, description="Department name")
    location: Optional[str] = Field(None, max_length=100, description="Location of the job")
    experience: Optional[str] = Field(None, max_length=100, description="Experience required for the job")
    description: Optional[str] = Field(None, max_length=100, description="small descripton aboout the job job")
    skills: List[str] = Field(..., description="Skills required for the job stored as a JSON array")
    status: JobDescriptionEnum = Field(default=JobDescriptionEnum.pending, description="Status of the job description")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")

    class Config:
        from_attributes = True


class JobDescriptionRequestorOutput(JobDescriptionRequest):
    id: int
    requestor_email: str


class JobDescriptionOutput(JobDescriptionRequest):
    id: int
    requestor_email: str
