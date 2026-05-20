from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#3498db"

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    focus_score: Optional[int] = Field(ge=1, le=10, default=5)
    note: Optional[str] = None
    goal: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class SessionUpdate(BaseModel):
    focus_score: Optional[int] = Field(ge=1, le=10, default=None)
    note: Optional[str] = None
    goal: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class SessionResponse(BaseModel):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    focus_score: int
    note: Optional[str]
    goal: Optional[str]
    tags: List[TagResponse]
    created_at: datetime

    class Config:
        from_attributes = True