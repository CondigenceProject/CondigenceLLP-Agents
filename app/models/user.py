from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    OWNER = "OWNER"
    OPERATIONS_MANAGER = "OPERATIONS_MANAGER"
    ACCOUNTS_ASSISTANT = "ACCOUNTS_ASSISTANT"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleEnum = RoleEnum.OWNER
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
