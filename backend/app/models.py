from sqlalchemy import Column, Integer, Float, String, DateTime
from .database import Base

class AthleteSettings(Base):
    __tablename__ = "athlete_settings"

    id = Column(Integer, primary_key=True, index=True)
    sex = Column(String, nullable=False, default="female")
    resting_hr = Column(Integer, nullable=False, default=65)
    max_hr = Column(Integer, nullable=False, default=195)

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    duration_s = Column(Float, nullable=False)
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    
    trimp = Column(Float, nullable=True)
    
    zone1_time = Column(Float, default=0.0)
    zone2_time = Column(Float, default=0.0)
    zone3_time = Column(Float, default=0.0)
    zone4_time = Column(Float, default=0.0)
    zone5_time = Column(Float, default=0.0)