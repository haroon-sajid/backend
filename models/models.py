from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

# -------------------------------
# Association table (Many-to-Many)
# -------------------------------
class TeamMemberLink(SQLModel, table=True):
    team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)

# -------------------------------
# User Model
# -------------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    email: str = Field(index=True, unique=True, max_length=100)
    password: str
    is_admin: bool = Field(default=False)
    role: Optional[str] = Field(default=None, max_length=100)

    # Many-to-many relationship with Team
    teams: List["Team"] = Relationship(back_populates="members", link_model=TeamMemberLink)

# -------------------------------
# Team Model
# -------------------------------
class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    created_by: int = Field(foreign_key="user.id")  # admin ID

    # Many-to-many relationship with User
    members: List[User] = Relationship(back_populates="teams", link_model=TeamMemberLink)

# -------------------------------
# Project Model
# -------------------------------
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    team_id: int = Field(foreign_key="team.id")
    created_by: int = Field(foreign_key="user.id")   # admin

# -------------------------------
# Task Model
# -------------------------------
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="To-Do")          # To-Do / In Progress / Completed
    project_id: int = Field(foreign_key="project.id")
    assigned_to: int = Field(foreign_key="user.id")  # member