from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from core.database import get_session
from models.models import Project, Task, User, TeamMemberLink, Team
from schemas.project_schema import ProjectCreate, ProjectRead
from schemas.task_schema import TaskCreate, TaskRead
from schemas.task_schema import TaskStatusUpdate
from pydantic import BaseModel, Field


router = APIRouter()


# -------------------------------
# Create Project with individual member tasks (New Bulk-Flow)
# -------------------------------
class MemberTaskIn(BaseModel):
    user_id: int
    task_title: str
    task_desc: str = ""


class ProjectWithTasksIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    team_id: int
    members: List[MemberTaskIn]


class ProjectWithTasksOut(BaseModel):
    project: ProjectRead
    tasks: List[TaskRead]


@router.post("/project_with_tasks", response_model=ProjectWithTasksOut)
def create_project_with_tasks(
    data: ProjectWithTasksIn,
    admin_id: int = 1,  # TODO auth
    session: Session = Depends(get_session)
):
    # verify admin belongs to team
    if not session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == data.team_id,
            TeamMemberLink.user_id == admin_id,
        )
    ).first():
        raise HTTPException(400, "Admin must be in the team")

    # 1. create project
    proj = Project(
        name=data.name,
        description=data.description,
        team_id=data.team_id,
        created_by=admin_id,
    )
    session.add(proj)
    session.commit()
    session.refresh(proj)

    # 2. create individual tasks
    tasks: List[Task] = []
    for row in data.members:
        t = Task(
            title=row.task_title,
            description=row.task_desc,
            project_id=proj.id,
            assigned_to=row.user_id,
        )
        session.add(t)
        tasks.append(t)
    session.commit()
    for t in tasks:
        session.refresh(t)

    return ProjectWithTasksOut(project=proj, tasks=tasks)

# -------------------------------
# Create Project
# -------------------------------
@router.post("/create_project", response_model=ProjectRead)
def create_project(
    data: ProjectCreate,
    admin_id: int = 1,               # TODO: replace with real auth user
    session: Session = Depends(get_session)
):
    # verify admin is in the team
    link = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == data.team_id,
            TeamMemberLink.user_id == admin_id
        )
    ).first()
    if not link:
        raise HTTPException(400, "Admin must be part of the team")

    proj = Project(
        name=data.name,
        description=data.description,
        team_id=data.team_id,
        created_by=admin_id
    )
    session.add(proj)
    session.commit()
    session.refresh(proj)
    return proj


# -------------------------------
# List Projects by Team
# -------------------------------
@router.get("/projects", response_model=List[ProjectRead])
def list_projects(team_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Project).where(Project.team_id == team_id)).all()


# -------------------------------
# Create Task inside Project
# -------------------------------
@router.post("/create_task", response_model=TaskRead)
def create_task(
    data: TaskCreate,
    project_id: int,
    session: Session = Depends(get_session)
):
    # verify assignee is member of the project team
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    member_link = session.exec(
        select(TeamMemberLink).where(
            TeamMemberLink.team_id == project.team_id,
            TeamMemberLink.user_id == data.assigned_to
        )
    ).first()
    if not member_link:
        raise HTTPException(400, "Assigned user must be a member of the project team")

    task = Task(
        title=data.title,
        description=data.description,
        project_id=project_id,
        assigned_to=data.assigned_to
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# -------------------------------
# Bulk Create Tasks (same title/desc for many members)
# -------------------------------
class BulkTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    assigned_to: List[int]          # array of member ids


@router.post("/bulk_tasks/{project_id}", response_model=List[TaskRead])
def bulk_create_tasks(
    project_id: int,
    data: BulkTaskCreate,
    session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # verify all users are actually members of the team
    team_id = project.team_id
    valid = session.exec(
        select(TeamMemberLink.user_id).where(
            TeamMemberLink.team_id == team_id,
            TeamMemberLink.user_id.in_(data.assigned_to)
        )
    ).all()
    if len(valid) != len(data.assigned_to):
        raise HTTPException(400, "One or more users are not in the project team")

    tasks = [
        Task(
            title=data.title,
            description=data.description,
            project_id=project_id,
            assigned_to=uid
        )
        for uid in data.assigned_to
    ]
    session.add_all(tasks)
    session.commit()
    for t in tasks:
        session.refresh(t)
    return tasks

# -------------------------------
# List Tasks (filter by user or project)
# -------------------------------
@router.get("/tasks", response_model=List[TaskRead])
def list_tasks(
    user_id: int | None = None,
    project_id: int | None = None,
    session: Session = Depends(get_session)
):
    query = select(Task)
    if user_id:
        query = query.where(Task.assigned_to == user_id)
    if project_id:
        query = query.where(Task.project_id == project_id)
    return session.exec(query).all()


# -------------------  NEW  -------------------
@router.patch("/tasks/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: "TaskStatusUpdate",
    user_id: int = 1,  # TODO: real auth
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    # ensure only assignee can update
    if task.assigned_to != user_id:
        raise HTTPException(403, "Not your task")
    task.status = payload.status
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


class TaskAdminRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    project_name: str
    team_name: str
    member_name: str


@router.get("/admin/tasks", response_model=list[TaskAdminRead])
def admin_tasks(session: Session = Depends(get_session)):
    rows = session.exec(
        select(
            Task.id,
            Task.title,
            Task.description,
            Task.status,
            Project.name.label("project_name"),
            Team.name.label("team_name"),
            User.name.label("member_name"),
        )
        .join(Project, Task.project_id == Project.id)
        .join(Team, Project.team_id == Team.id)
        .join(User, Task.assigned_to == User.id)
    ).all()
    return [TaskAdminRead(**r._mapping) for r in rows]


class TaskMemberRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    project_name: str


@router.get("/member/tasks", response_model=list[TaskMemberRead])
def member_tasks(user_id: int, session: Session = Depends(get_session)):
    rows = session.exec(
        select(
            Task.id,
            Task.title,
            Task.description,
            Task.status,
            Project.name.label("project_name"),
        )
        .join(Project, Task.project_id == Project.id)
        .where(Task.assigned_to == user_id)
    ).all()
    return [TaskMemberRead(**r._mapping) for r in rows]
