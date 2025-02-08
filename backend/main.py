from typing import Annotated

import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException
from models import Tasks
from sqlalchemy.orm import Session

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

@app.get("/")
async def read_all(db: db_dependecy):
    return db.query(Tasks).all()

@app.get("/task/{task_id}")
async def get_task_id(db: db_dependecy, task_id: int):
    task_model = db.query(Tasks).filter(Tasks.id == task_id).first()
    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404, detail="Task not found")
