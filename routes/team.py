from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from core.database import get_session
from models.models import User, Team, TeamMemberLink
from schemas.team_schema import TeamCreate, TeamRead, TeamReadWithCreator

router = APIRouter()  

# -------------------------------
# Create a Team and Add Members
# -------------------------------
@router.post("/create_team", response_model=TeamRead)
def create_team(team_data: TeamCreate, session: Session = Depends(get_session)):
    """
    Admin creates a team and adds registered members.
    """
    #  Validate member IDs
    members = session.exec(select(User).where(User.id.in_(team_data.member_ids))).all()
    if len(members) != len(team_data.member_ids):
        raise HTTPException(status_code=400, detail="One or more user IDs are invalid")

    #  Create team
    new_team = Team(
        name=team_data.name,
        description=team_data.description,
        created_by=1  # TODO: replace with actual admin ID from auth session
    )
    session.add(new_team)
    session.commit()
    session.refresh(new_team)

    #  Link members (many-to-many)
    for member in members:
        link = TeamMemberLink(team_id=new_team.id, user_id=member.id)
        session.add(link)
    session.commit()

    #  Return response
    return TeamRead(
        id=new_team.id,
        name=new_team.name,
        description=new_team.description,
        created_by=new_team.created_by,
        member_ids=team_data.member_ids
    )

# -------------------------------
# List All Teams with Members
# -------------------------------
@router.get("/teams_list", response_model=list[TeamReadWithCreator])
def list_teams(session: Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    result = []
    for team in teams:
        member_links = session.exec(
            select(TeamMemberLink).where(TeamMemberLink.team_id == team.id)
        ).all()
        member_ids = [link.user_id for link in member_links]
        creator = session.get(User, team.created_by)
        result.append(
            TeamReadWithCreator(
                id=team.id,
                name=team.name,
                description=team.description,
                created_by_name=creator.name if creator else "Unknown",
                member_ids=member_ids,
            )
        )
    return result
