from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(Boolean, default=False)
    priority = Column(Integer)
    owner_id = Column(Integer, ForeignKey("Users.id"))


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    status = Column(Boolean, default=True)
    hashed_password = Column(String)
    role = Column(String)
    phone_number = Column(String)
    