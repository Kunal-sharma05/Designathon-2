from pydantic import BaseModel, Field
from model.user_role import UserRole
import logging

logger = logging.getLogger(__name__)


class UserDetailsRequest(BaseModel):
    name: str = Field(min_length=5)
    email: str = Field(min_length=10, description="""The email starts with alphanumeric characters, dots, underscores, percent signs, plus signs, or hyphens.
                                                                                                                It contains an "@" symbol followed by a domain name.
                                                                                                                The domain name is followed by a dot and a top-level domain (TLD) with at least two characters.""")
    password: str = Field(min_length=8, description="""The password is at least 8 characters long.
                                                                    It contains at least one letter and one number.""")
    role: UserRole

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    email: str
    password: str
