from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from model.JobDescriptionEnum import JobDescriptionEnum


class JobDescriptionRequest(BaseModel):
    id: str = Field(..., description="UUID of the job description")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the job description")
    department: Optional[str] = Field(None, max_length=100, description="Department name")
    location: Optional[str] = Field(None, max_length=100, description="Location of the job")
    experience: Optional[str] = Field(None, max_length=100, description="Experience required for the job")
    skills: List[str] = Field(..., description="Skills required for the job stored as a JSON array")
    requestor_email: Optional[str]
    status: JobDescriptionEnum = Field(default=JobDescriptionEnum.pending, description="Status of the job description")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    user_id: Optional[str] = Field(None, description="Foreign key to the user details table")

    class Config:
        from_attributes = True
