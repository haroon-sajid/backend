from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    team_id: int


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    team_id: int
    created_by: int

    model_config = {"from_attributes": True}


