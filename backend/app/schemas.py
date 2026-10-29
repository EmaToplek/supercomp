"""
Pydantic schemas: what the API accepts and returns.

They validate incoming JSON and control which fields are sent back, separately from the SQLAlchemy models in models.py.
"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class SettingsSchema(BaseModel):
    """Athlete settings used for HR zones and TRIMP."""

    model_config = ConfigDict(from_attributes=True) 

    sex: Literal["female", "male"]
    resting_hr: int = Field(ge=30, le=120)
    max_hr: int = Field(ge=120, le=230)

    @model_validator(mode="after")
    def check_hr_order(self):
        if self.resting_hr >= self.max_hr:
            raise ValueError("resting_hr must be lower than max_hr")
        return self