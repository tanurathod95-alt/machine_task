from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.database import get_session
from app.models.user import User
from app.auth import authenticate
from app.services.auth_services import signup_user,login_user

router = APIRouter(prefix="/auth",tags=["Authentication"])
# 1. SIGNUP
@router.post("/signup",status_code=status.HTTP_201_CREATED)
def signup(
    name: str,
    email: str,
    password: str,
    session: Session = Depends(get_session)
):

    user = signup_user(session=session,name=name,email=email,password=password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")

    return {
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

#Login
@router.post("/login")
def login(
    email: str,
    password: str,
    session: Session = Depends(get_session)
):
    token = login_user(session=session,email=email,password=password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )
    return {
        "access_token": token,
        "token_type": "bearer"
    }

#Profile
@router.get("/profile")
def get_profile(
    current_user: dict = Depends(authenticate),
    session: Session = Depends(get_session)
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user ID missing"
        )
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    user = session.get(User,user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }