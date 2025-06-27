from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from db.database import base
from sqlalchemy.orm import relationship
from datetime import datetime
from model.NotificationEnum import NotificationStatusEnum

class Notification(base):
    __tablename__ = 'notifications'
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)  # UUID
    job_description_id = Column(ForeignKey("job_descriptions.id"))  # foreign key to job_descriptions.id
    workflow_status_id = Column(ForeignKey("workflow_statuses.id"))
    recipient_email = Column(String(255), nullable=False)
    status = Column(Enum(NotificationStatusEnum), default=NotificationStatusEnum.pending)
    sent_at = Column(DateTime)
    workflow_status = relationship("WorkflowStatus",back_populates="notifications")