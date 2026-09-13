from pydantic import BaseModel
from typing import List, Optional


class DailyCheckIn(BaseModel):
    sleep_hours: Optional[float] = None
    energy_level: Optional[int] = None
    tasks: List[str] = []
    commitments: List[str] = []
    notes: Optional[str] = None
    