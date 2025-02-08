from database import Base
from sqlalchemy import Boolean, Column, Integer, String


class Tasks(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(Boolean, default=False)
    priority = Column(Integer)
