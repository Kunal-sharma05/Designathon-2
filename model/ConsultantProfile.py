from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from model.ConsultantEnum import ConsultantEnum
from db.database import base
from datetime import datetime

class ConsultantProfile(base):
    __tablename__ = 'consultant_profiles'
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)  # UUID
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    skills = Column(JSON)  # Stored as JSON array
    experience = Column(Integer)  # in years
    location = Column(String(100))
    project = Column(String(1000))
    availability = Column(Enum(ConsultantEnum), default=ConsultantEnum.available)
    created_at = Column(DateTime, default=datetime.now)