from pydantic import BaseModel, Field
from model.user_role import UserRole


class UserDetailsRequest(BaseModel):
    name: str = Field(min_length=5)
    email: str = Field(min_length=10, pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", description="""The email starts with alphanumeric characters, dots, underscores, percent signs, plus signs, or hyphens.
                                                                                                                It contains an "@" symbol followed by a domain name.
                                                                                                                The domain name is followed by a dot and a top-level domain (TLD) with at least two characters.""")
    password: str = Field(min_length=8, pattern="^[A-Za-z0-9]{8,}$", description="""The password is at least 8 characters long.
                                                                    It contains at least one letter and one number.""")
    role: UserRole
