from fastapi import (APIRouter,Depends,HTTPException,status)
from fastapi.security import (HTTPBearer,HTTPAuthorizationCredentials)
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User

from app.services.auth_services import (signup_user,login_user)

from app.auth import verify_token


router = APIRouter(prefix="/auth",tags=["Authentication"])
security = HTTPBearer()
# 1.SIGNUP API

@router.post("/signup")
def signup(name: str,email: str,password: str,session: Session = Depends(get_session)):

    user = signup_user(session=session,name=name,email=email,password=password)

    if not user:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")

    return {"message": "User registered successfully","user_id": user.id,"name": user.name,"email": user.email}
# 2. LOGIN API

@router.post("/login")
def login(email: str,password: str,session: Session = Depends(get_session)):

    token = login_user(session=session,email=email,password=password)

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password")

    return {"message": "Login successful","access_token": token,"token_type": "bearer"}



# 3. GET PROFILE API

@router.get("/profile")
def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security),session: Session = Depends(get_session)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    user = session.exec(select(User).where(User.id == int(user_id))).first()

    if not user:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    return {"id": user.id,"name": user.name,"email": user.email}

