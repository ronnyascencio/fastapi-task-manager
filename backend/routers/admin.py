from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from models import Tasks
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]




@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    else:
        user.get('user_role') != 'admin'
        return db.query(Tasks).all()
        
        