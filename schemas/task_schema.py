from pydantic import BaseModel, Field
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    assigned_to: int          # member id


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    project_id: int
    assigned_to: int

    model_config = {"from_attributes": True}


class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(To-Do|In Progress|Completed)$")


