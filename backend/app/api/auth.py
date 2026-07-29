import os
import psycopg
from fastapi import APIRouter, HTTPException

from app.api.auth_schemas import LoginRequest, LoginResponse
from app.core.security import verify_password, create_access_token

router = APIRouter()
DB_URL = os.environ["DATABASE_URL"]


@router.post("/api/v1/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, password_hash, role, full_name, is_active FROM admin_users WHERE email = %s",
                (request.email,),
            )
            row = cur.fetchone()

    # Same error for "no such email" and "wrong password" on purpose —
    # telling an attacker which one was wrong makes it easier to
    # enumerate real staff email addresses. Standard login-form practice.
    invalid_creds = HTTPException(status_code=401, detail="Invalid email or password")

    if not row:
        raise invalid_creds

    user_id, password_hash, role, full_name, is_active = row

    if not is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled")

    if not verify_password(request.password, password_hash):
        raise invalid_creds

    token = create_access_token(data={"sub": str(user_id), "role": role})
    return LoginResponse(access_token=token, role=role, full_name=full_name)