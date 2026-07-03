from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings
from app.models import UserResponse

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer(auto_error=False)

_users_db: Dict[str, dict] = {
    "admin": {
        "password": pwd_context.hash("admin123"),
        "email": "admin@example.com",
        "created_at": datetime.now(),
        "is_active": True
    },
    "user": {
        "password": pwd_context.hash("user123"),
        "email": "user@example.com",
        "created_at": datetime.now(),
        "is_active": True
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user(username: str) -> Optional[dict]:
    return _users_db.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    if not user.get("is_active", True):
        return None
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return UserResponse(
        username=username,
        email=user.get("email"),
        created_at=user.get("created_at", datetime.now()),
        is_active=user.get("is_active", True)
    )


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None