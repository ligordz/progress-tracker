from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GoalCreate(BaseModel):
    title: str
    target_minutes: float = Field(gt=0)
    deadline: Optional[datetime] = None

class GoalResponse(BaseModel):
    id: int
    title: str
    target_minutes: float
    achieved_minutes: float  # Рассчитывается динамически
    progress_percent: float  # 0-100
    deadline: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True