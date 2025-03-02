from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers import admin, auth, task, users

app = FastAPI()

"""
database creation

"""
Base.metadata.create_all(bind=engine)

""" router settings """
@app.get('/healthy')
def healthy_check():
    return {'status': 'healthy'}


app.include_router(auth.router)
app.include_router(task.router)
app.include_router(admin.router)
app.include_router(users.router)