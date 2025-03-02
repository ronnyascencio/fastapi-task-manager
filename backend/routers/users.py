from typing import Annotated

from ..database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from ..models import Users
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)
    
    
class UserPhoneVerification(BaseModel):
    phone_number_update: str = Field(min_length=10, max_length=15)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail='No user login')
    return db.query(Users).filter(Users.id == user.get('id')).first()






@router.put("/change_pass", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, 
                          password_request: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    
    if not bcrypt_context.verify(password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=404, detail='No password found')
    user_model.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.add(user_model)
    db.commit()


@router.put('/phonenumber/{phone_number}', status_code=status.HTTP_200_OK)
async def update_phone_number(user: user_dependency, db: db_dependency, phone_request: UserPhoneVerification, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    
    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()