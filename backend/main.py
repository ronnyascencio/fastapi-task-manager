from typing import Annotated
from starlette import status
import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Path
from models import Tasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field



app = FastAPI()

"""
database creation

"""
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()

db_dependecy = Annotated[Session, Depends(get_db)]

""" pydantic derequest """

class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(max_length=100)
    status: bool
    priority: int = Field(gt=0, lt=6)





""" GETS FUNCTIONS, GETTING ALL TASKS AND GETTING A TASK BY ID  FROM DATABASE """


@app.get("/")
async def read_all(db: db_dependecy, status_code=status.HTTP_200_OK):
    return db.query(Tasks).all()

@app.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(db: db_dependecy, task_id: int = Path(gt=0)):
    task_model = db.query(Tasks).filter(Tasks.id == task_id).first()
    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404, detail="Task not found")





""" POST AND UPDATE FUNCTIONS, CREATING A TASK AND ADDING IT TO THE DATA BASE"""

@app.post("/task", status_code=status.HTTP_201_CREATED)
async def post_task(db: db_dependecy, task_request: TaskRequest):
    task_model = Tasks(**task_request.model_dump())
    db.add(task_model)
    db.commit()

@app.put("/task/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_id(db: db_dependecy, task_id: int, task_request: TaskRequest):
    task_model = db.query(Tasks).filter(Tasks.id == task_id).first()
    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_model.title = task_request.title
    task_model.description = task_request.description
    task_model.priority = task_request.priority
    task_model.status = task_request.status

    db.add(task_model)
    db.commit()

""" DELETE FUNCTIONS, DELETE TASK  BY SEARCHING THE TASK BY ID OR TITLE"""
