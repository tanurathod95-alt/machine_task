from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.models.user import User


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not configured in .env file"
    )


# =========================================================
# PASSWORD CONFIGURATION
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================================================
# PASSWORD HASH
# =========================================================

def hash_password(password: str) -> str:

    return pwd_context.hash(password)


# =========================================================
# PASSWORD VERIFY
# =========================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# =========================================================
# CREATE ACCESS TOKEN
# =========================================================

def create_access_token(
    data: dict,
    expires_minutes: int = 60
) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes
    )

    to_encode.update({
        "exp": expire
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# =========================================================
# SIGNUP USER
# =========================================================

def signup_user(
    session: Session,
    name: str,
    email: str,
    password: str
):

    # Check existing user
    existing_user = session.exec(
        select(User).where(
            User.email == email
        )
    ).first()

    if existing_user:
        return None

    # Hash password
    hashed_password = hash_password(password)

    # Create user
    user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    session.add(user)

    session.commit()

    session.refresh(user)

    return user


# =========================================================
# LOGIN USER
# =========================================================

def login_user(
    session: Session,
    email: str,
    password: str
):

    # Find user
    user = session.exec(
        select(User).where(
            User.email == email
        )
    ).first()

    if not user:
        return None

    # Verify password
    password_valid = verify_password(
        password,
        user.password
    )

    if not password_valid:
        return None

    # Create JWT
    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return token