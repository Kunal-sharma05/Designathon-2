from pydantic import BaseModel


class JobDescriptionRequest(BaseModel):
    title: str
    skill_required: str
    experience: int
    description: str
    package: str
    location: str