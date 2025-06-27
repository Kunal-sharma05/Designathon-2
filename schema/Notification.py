from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from model.NotificationEnum import NotificationStatusEnum


class NotificationSchema(BaseModel):
    job_description_id: str = Field(..., description="Foreign key to the job description ID")
    recipient_email: str = Field(
        ...,
        min_length=10,
        pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$",
        description="""The email starts with alphanumeric characters, dots, underscores, percent signs, plus signs, or hyphens.
                       It contains an "@" symbol followed by a domain name.
                       The domain name is followed by a dot and a top-level domain (TLD) with at least two characters."""
    )
    status: NotificationStatusEnum = Field(default=NotificationStatusEnum.pending, description="Notification status")
    sent_at: Optional[datetime] = Field(None, description="Timestamp when the notification was sent")

    class Config:
        from_attributes = True
