from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""Data base """


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependecy = Annotated[Session, Depends(get_db)]

""" pydantic derequest """


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    password: str = Field(min_length=6)


@router.get("/auth/")
async def read_all(db: db_dependecy, status_code=status.HTTP_200_OK):
    return db.query(Users).all()


@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependecy, create_user_request: CreateUserRequest):
    user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        status=True,
    )
    db.add(user_model)
    db.commit()
