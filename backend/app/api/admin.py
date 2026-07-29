from fastapi import APIRouter, Depends
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/api/v1/admin/me")
def read_current_admin(current_user: dict = Depends(get_current_user)):
    return current_user