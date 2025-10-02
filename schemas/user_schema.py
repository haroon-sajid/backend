from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    # is_admin: Optional[bool] = False
    is_admin: bool = False
    role: Optional[str] = None


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool
    role: Optional[str] = None

    # allow reading attributes from ORMs / SQLModel instances
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str
