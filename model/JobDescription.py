from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import base
from model.JobDescriptionEnum import JobDescriptionEnum
class JobDescription(base):
    __tablename__ = 'job_descriptions'
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)  # UUID
    title = Column(String(255), nullable=False)
    department = Column(String(100))
    location = Column(String(100))
    experience = Column(String(100))
    skills = Column(JSON)  # Stored as JSON array
    requestor_email = Column(String(255))
    status = Column(Enum(JobDescriptionEnum), default=JobDescriptionEnum.pending)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(ForeignKey("user_details.id"))
    users = relationship("UserDetails", back_populates="job_descriptions")
    matched_results = relationship("MatchResult", back_populates="job_description",cascade="all,delete-orphan")
    workflow_status = relationship("WorkflowStatus", back_populates="job_description", cascade="all,delete-orphan")
