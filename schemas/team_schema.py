from pydantic import BaseModel, Field
from typing import Optional, List

class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    member_ids: List[int] = []  # IDs of registered users to add

class TeamRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    member_ids: List[int] = []

    # allow reading attributes from ORM / SQLModel
    model_config = {"from_attributes": True}


class TeamReadWithCreator(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by_name: str
    member_ids: List[int] = []

    model_config = {"from_attributes": True}