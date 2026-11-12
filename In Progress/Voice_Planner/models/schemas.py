from pydantic import BaseModel
from typing import List, Optional


class Commitment(BaseModel):
    activity: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class DailyCheckIn(BaseModel):
    sleep_hours: Optional[float] = None
    energy_level: Optional[int] = None
    tasks: List[str] = []
    commitments: List[Commitment] = []
    notes: Optional[str] = None