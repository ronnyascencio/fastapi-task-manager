from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLAlCHEMY_DATABASE_URL = "postgresql://postgres:1234!@localhost/taskmanagerAppDatabase"

engine = create_engine(
    SQLAlCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
