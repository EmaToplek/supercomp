from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship


class AthleteSettings(Base):
    __tablename__ = "athlete_settings"

    id = Column(Integer, primary_key=True)
    sex = Column(String, nullable=False, default="female")
    resting_hr = Column(Integer, nullable=False, default=65)
    max_hr = Column(Integer, nullable=False, default=195)


class Activity(Base):
    """One uploaded workout with its computed metrics"""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_s = Column(Float, nullable=False)
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)

    trimp_banister = Column(Float, nullable=True)
    trimp_edwards = Column(Float, nullable=True)

    # Time in each HR zone, in seconds
    zone1_time = Column(Float, default=0.0)
    zone2_time = Column(Float, default=0.0)
    zone3_time = Column(Float, default=0.0)
    zone4_time = Column(Float, default=0.0)
    zone5_time = Column(Float, default=0.0)

    samples = relationship(
        "ActivitySample", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivitySample(Base):
    """Raw per-record data from the FIT file, kept so metrics can be recalculated"""

    __tablename__ = "activity_samples"

    id = Column(Integer, primary_key=True)
    activity_id = Column(
        Integer,
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    heart_rate = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    distance = Column(Float, nullable=True)

    activity = relationship("Activity", back_populates="samples")
