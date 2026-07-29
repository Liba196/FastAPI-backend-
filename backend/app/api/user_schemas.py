from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # validated against allowed values in the route itself


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    # Deliberately no password_hash field here — Pydantic only returns
    # what's declared, so even if we accidentally selected it from the
    # DB, it could never leak out through this response model.