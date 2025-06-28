from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from model.WorkflowEnum import WorkflowProgressEnum
import logging
logger = logging.getLogger(__name__)


class WorkflowStatusSchema(BaseModel):
    job_description_id: str = Field(..., description="Foreign key to the job description ID")
    progress: WorkflowProgressEnum = Field(default=WorkflowProgressEnum.PENDING, description="Current progress of the workflow")
    started_at: datetime = Field(default_factory=datetime.now, description="Timestamp when the workflow started")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when the workflow was completed")
    steps: Dict[str, bool] = Field(..., description="JSON object representing the steps and their completion status")

    class Config:
        from_attributes = True
