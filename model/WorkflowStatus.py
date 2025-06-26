from db.database import base
from sqlalchemy import Column, Integer, Enum, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import VARCHAR
from model.user_role import UserRole
from datetime import datetime
from model.WorkflowEnum import WorkflowProgressEnum


class WorkflowStatus(base):
    __tablename__ = 'workflow_statuses'
    __allow_unmapped__ = True

    id = Column(String(36), primary_key=True)  # UUID
    job_description_id = Column(ForeignKey("job_descriptions.id")) # foreign key to job_descriptions.id
    progress = Column(Enum(WorkflowProgressEnum), default=WorkflowProgressEnum.PENDING)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    steps = Column(JSON)  # e.g., {"jd_parsed": true, "profiles_compared": false}
    job_description = relationship("JobDescription", back_populates="workflow_status")
    notifications = relationship("Notification", back_populates="workflow_status", cascade="all,delete-orphan")