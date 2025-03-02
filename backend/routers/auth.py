from datetime import datetime, timedelta, timezone
from typing import Annotated

from ..database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from ..models import Users
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter( prefix="/auth", tags=["auth"])

SECRET_KEY = "00dd1dd7df0dd87eae9acf1cf622d22c381a3f339b27d34aad911da34f1df161"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oa2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

"""Data base """


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[Session, Depends(get_db)]



"""User auth functions"""

def user_auth(user_name: str, password: str, db,):
    user = db.query(Users).filter(Users.username == user_name).first()
    
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_data: timedelta):
    if not Users.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User role not found")

    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_data
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



    
async def get_current_user(token: Annotated[str, Depends(oa2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail='could not validate credentials')
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail='could not validate credentials')
    



""" pydantic dependency request """


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    password: str = Field(min_length=6)
    phone_number: str = Field(min_length=10, max_length=15)




class Token(BaseModel):
    access_token: str
    token_type: str


    

@router.get("/")
async def read_all(db: db_dependency, status_code=status.HTTP_200_OK):
    return db.query(Users).all()


@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        status=True,
    )
    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    
    user = user_auth(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail='could not validate credentials')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': "bearer"}






