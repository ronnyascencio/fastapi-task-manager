from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Tasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from .auth import get_current_user

router = APIRouter(prefix="/task", tags=["task"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

""" pydantic dependency request """


class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(max_length=100)
    status: bool
    priority: int = Field(gt=0, lt=6)


""" GETS FUNCTIONS, GETTING ALL TASKS AND GETTING A TASK BY ID  FROM DATABASE """


@router.get("/")
async def read_all(user: user_dependency, db: db_dependency, status_code=status.HTTP_200_OK):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    return db.query(Tasks).all()


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(user: user_dependency, db: db_dependency, task_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = db.query(Tasks).filter(Tasks.id == task_id)\
        .filter(Tasks.owner_id == user.get('id')).first()
    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404, detail="Task not found")



@router.get("/{owner_id}", status_code=status.HTTP_200_OK)
async def get_task_by_owner_id(user: user_dependency, 
                               db: db_dependency, owner_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = db.query(Tasks).filter(Tasks.owner_id == user.get('id')).all()
    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404, detail="Task not found")


""" POST AND UPDATE FUNCTIONS, CREATING A TASK AND ADDING IT TO THE DATA BASE"""


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def post_task(user: user_dependency, 
                    db: db_dependency, task_request: TaskRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = Tasks(**task_request.model_dump(), owner_id=user.get('id'))
    db.add(task_model)
    db.commit()


@router.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_id(user: user_dependency, db: db_dependency, 
                         task_id: int, 
                         task_request: TaskRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = db.query(Tasks).filter(Tasks.id == task_id)\
        .filter(Tasks.owner_id == user.get('id')).first()
    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_model.title = task_request.title
    task_model.description = task_request.description
    task_model.priority = task_request.priority
    task_model.status = task_request.status
    

    db.add(task_model)
    db.commit()


""" DELETE FUNCTIONS, DELETE TASK  BY SEARCHING THE TASK BY ID OR TITLE"""


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(user: user_dependency, db: db_dependency, task_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = db.query(Tasks).filter(Tasks.id == task_id)\
        .filter(Tasks.owner_id == user.get('id')).first()
    if task_model is None:
        raise HTTPException(status_code=404, detail="task not found")
    db.query(Tasks).filter(Tasks.id == task_id)\
        .filter(Tasks.owner_id == user.get('id')).delete()
    db.commit()



@router.delete(
    "/title/{task_title}", status_code=status.HTTP_204_NO_CONTENT
)  # Distinct path
async def delete_task_by_title(user: user_dependency, db: db_dependency, task_title: str):
    if user is None:
        raise HTTPException(status_code=401, detail="authentication failed")
    task_model = db.query(Tasks).filter(Tasks.title == task_title)\
        .filter(Tasks.owner_id == user.get('id')).first()

    if task_model is None:
        raise HTTPException(
            status_code=404, detail="Task title was wrong and task not found"
        )

    db.query(Tasks).filter(Tasks.title == task_title)\
        .filter(Tasks.owner_id == user.get('id')).delete()
    db.commit()
