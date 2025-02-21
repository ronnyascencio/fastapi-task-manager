from fastapi import APIRouter
from models import Users
from pydantic import BaseModel

router = APIRouter()


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    password: str


@router.post("/auth/")
async def create_user(create_user_request: CreateUserRequest):
    user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=create_user_request.password,
        status=True,
    )

    return user_model
