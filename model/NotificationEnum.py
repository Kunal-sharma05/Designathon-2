from enum import Enum

class NotificationStatusEnum(str, Enum):
    sent = "sent"
    failed = "failed"
    pending = "pending"