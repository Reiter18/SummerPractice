from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta

from app.models import UserLogin, TokenResponse, UserRegister, UserResponse
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    _users_db
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    user = authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user_login.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    from datetime import datetime
    _users_db[user_data.username] = {
        "password": get_password_hash(user_data.password),
        "email": user_data.email,
        "created_at": datetime.now(),
        "is_active": True
    }

    return UserResponse(
        username=user_data.username,
        email=user_data.email,
        created_at=datetime.now(),
        is_active=True
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    return {"message": f"User {current_user.username} logged out successfully"}


@router.get("/verify")
async def verify_token(current_user: UserResponse = Depends(get_current_user)):
    return {"valid": True, "user": current_user.username}