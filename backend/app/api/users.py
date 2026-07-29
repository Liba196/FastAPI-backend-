import os
import psycopg
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.user_schemas import CreateUserRequest, UpdateUserRequest, UserResponse
from app.core.deps import require_role, get_current_user
from app.core.security import hash_password

router = APIRouter()
DB_URL = os.environ["DATABASE_URL"]
VALID_ROLES = ("super_admin", "it_admin", "content_editor")


@router.post("/api/v1/admin/users", response_model=UserResponse, status_code=201)
def create_user(payload: CreateUserRequest, _: dict = Depends(require_role("super_admin"))):
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {VALID_ROLES}")

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM admin_users WHERE email = %s", (payload.email,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail="An account with this email already exists")

            cur.execute(
                """
                INSERT INTO admin_users (email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id, email, full_name, role, is_active, created_at
                """,
                (payload.email, hash_password(payload.password), payload.full_name, payload.role),
            )
            row = cur.fetchone()
        conn.commit()

    # Safety check: ensure row data was successfully created and returned
    if not row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user record."
        )

    return UserResponse(id=row[0], email=row[1], full_name=row[2], role=row[3], is_active=row[4], created_at=row[5])


@router.get("/api/v1/admin/users", response_model=list[UserResponse])
def list_users(_: dict = Depends(require_role("super_admin"))):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, full_name, role, is_active, created_at FROM admin_users ORDER BY id")
            rows = cur.fetchall()

    return [
        UserResponse(id=r[0], email=r[1], full_name=r[2], role=r[3], is_active=r[4], created_at=r[5])
        for r in rows
    ]


@router.patch("/api/v1/admin/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    current_user: dict = Depends(require_role("super_admin")),
):
    if str(user_id) == current_user["user_id"] and (payload.role or payload.is_active is False):
        raise HTTPException(status_code=400, detail="You cannot change your own role or deactivate your own account")

    if payload.role and payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"role must be one of {VALID_ROLES}")

    fields, values = [], []
    if payload.full_name is not None:
        fields.append("full_name = %s")
        values.append(payload.full_name)
    if payload.role is not None:
        fields.append("role = %s")
        values.append(payload.role)
    if payload.is_active is not None:
        fields.append("is_active = %s")
        values.append(payload.is_active)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    values.append(user_id)

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE admin_users SET {', '.join(fields)} WHERE id = %s "
                f"RETURNING id, email, full_name, role, is_active, created_at",
                values,
            )
            row = cur.fetchone()
            
            # Safety check: handles case where user_id does not exist in database
            if not row:
                raise HTTPException(status_code=404, detail="User not found")
        conn.commit()

    return UserResponse(id=row[0], email=row[1], full_name=row[2], role=row[3], is_active=row[4], created_at=row[5])


@router.delete("/api/v1/admin/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    current_user: dict = Depends(require_role("super_admin")),
):
    # Guard rail: Prevent a super_admin from deleting their own account
    if str(user_id) == current_user["user_id"]:
        raise HTTPException(
            status_code=400, 
            detail="You cannot delete your own admin account"
        )

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # 1. Execute the delete query and check if the user existed
            cur.execute(
                "DELETE FROM admin_users WHERE id = %s RETURNING id", 
                (user_id,)
            )
            row = cur.fetchone()
            
            # 2. If no row was returned, the user ID didn't exist
            if not row:
                raise HTTPException(
                    status_code=404, 
                    detail="User not found"
                )
        conn.commit()

    # HTTP 204 means successful deletion with no content returned
    return None










