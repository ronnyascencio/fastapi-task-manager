from datetime import datetime, timedelta, timezone
from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter()

SECRET_KE = "00dd1dd7df0dd87eae9acf1cf622d22c381a3f339b27d34aad911da34f1df161"
ALGOITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""Data base """


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependecy = Annotated[Session, Depends(get_db)]


"""User auth functions"""

def user_auth(user_name: str, password: str, db,):
    user = db.query(Users).filter(Users.username == user_name).first()
    
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_acces_token(username: str, user_id: int, expires_data: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_data
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KE, algorithm=ALGOITHM)
    

""" pydantic derequest """


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    password: str = Field(min_length=6)




class Token(BaseModel):
    access_token: str
    token_type: str



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


@router.post("/token", response_model=Token)
async def login_acces_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependecy):
    
    user = user_auth(form_data.username, form_data.password, db)
    if not user:
        return "there is no user or pasword"
    token = create_acces_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': "bearer"}
    