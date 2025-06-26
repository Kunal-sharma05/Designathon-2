from enum import Enum

class ConsultantEnum(str, Enum):
    available = "available"
    busy = "busy"
    unavailable = "unavailable"