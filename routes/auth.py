from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from models.models import User
from schemas.user_schema import UserCreate, UserRead, UserLogin
from core.database import get_session
from passlib.context import CryptContext

#  Simple router, no prefix
router = APIRouter(tags=["Authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt 72 char max support karta hai
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

# -------------------------------
# Helper functions
# -------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# -------------------------------
# Signup Route
# -------------------------------
@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    # Check if email already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Create and save user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        is_admin=user.is_admin
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

# -------------------------------
# Login Route
# -------------------------------
@router.post("/login", response_model=UserRead)
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email."
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The password you entered is incorrect."
        )

    return db_user

# -------------------------------
# user-list Route
# -------------------------------

@router.get("/users_list", response_model=list[UserRead])
def users_list(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()
