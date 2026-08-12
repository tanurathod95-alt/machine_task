from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.models.user import User

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# PASSWORD FUNCTIONS

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str,hashed_password: str) -> bool:

    return pwd_context.verify(plain_password,hashed_password)

# JWT TOKEN


def create_access_token(data: dict,expires_minutes: int = 60) -> str:

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

# SIGNUP


def signup_user(session: Session,name: str,email: str,password: str):

    existing_user = session.exec(select(User).where(User.email == email)).first()

    if existing_user:
        return None
    
    hashed_password = hash_password(password)

    user = User(name=name,email=email,password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user

# LOGIN


def login_user(session: Session,email: str,password: str):

    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        return None

    password_valid = verify_password(password,user.password)

    if not password_valid:
        return None

    token = create_access_token({"sub": str(user.id)})

    return token