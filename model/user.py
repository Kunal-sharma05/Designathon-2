from db.database import base
from sqlalchemy import Column, Integer, Enum
from sqlalchemy.dialects.mysql import VARCHAR
from model.user_role import UserRole


class UserDetails(base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(250))
    email = Column(VARCHAR(250), unique=True)
    password = Column(VARCHAR(250))
    role = Column(Enum(UserRole))
