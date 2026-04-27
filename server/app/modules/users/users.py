from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/")
def read_users():
    return {"message": "List of users"}