from db.database import base
from sqlalchemy import Column, Integer, Enum, Float
from sqlalchemy.dialects.mysql import  VARCHAR

class JobDescription(base):
    __tablename__="job_description"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(VARCHAR(250))
    skill_required = Column(VARCHAR(250))
    experience = Column(Integer)
    description = Column(VARCHAR(500))
    package = Column(VARCHAR(100))
    location = Column(VARCHAR(250))
