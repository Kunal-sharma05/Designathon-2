from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.database import base
from datetime import datetime

class MatchResult(base):
    __tablename__ = 'matches'
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True)  # UUID
    job_description_id = Column(ForeignKey("job_descriptions.id"))  # foreign key to job_descriptions.id
    consultant_id = Column(ForeignKey("consultant_profiles.id"))  # foreign key to consultant_profiles.id
    similarity_score = Column(Float)  # float between 0.0 - 1.0
    rank = Column(Integer, nullable=False)
    matched_at = Column(DateTime, default=datetime.now)
    job_description = relationship("JobDescription", back_populates="matched_results", uselist=False)