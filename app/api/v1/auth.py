from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import Token, UserResponse
from app.core.security import create_access_token, get_current_user_optional
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory mock user store for fast development
MOCK_USERS = {
    "admin": {
        "id": "usr_01",
        "username": "admin",
        "email": "owner@condigence.com",
        "full_name": "Admin",
        "role": "OWNER",
        "password_hash": "admin123"
    },
    "ops_manager": {
        "id": "usr_02",
        "username": "ops_manager",
        "email": "ops@condigence.com",
        "full_name": "Operations Manager",
        "role": "OPERATIONS_MANAGER",
        "password_hash": "ops123"
    }
}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = MOCK_USERS.get(form_data.username)
    if not user or user["password_hash"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "id": user["id"]},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"]
    }


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user_optional)):
    return current_user
