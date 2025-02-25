import models
from database import engine
from fastapi import FastAPI
from routers import admin, auth, task

app = FastAPI()

"""
database creation

"""
models.Base.metadata.create_all(bind=engine)

""" router settings """

app.include_router(auth.router)
app.include_router(task.router)
app.include_router(admin.router)