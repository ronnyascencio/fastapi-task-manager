from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app
from ..routers.task import get_current_user, get_db
import pytest
from ..models import Tasks

SQLAlCHEMY_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLAlCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close_all()


def override_get_current_user():
    return {"username": "rascenciotest", "id": 1, "role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)


@pytest.fixture
def test_task():
    task = Tasks(
        title="Test task",
        description="Test task description",
        priority=5,
        status=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(task)
    db.commit()
    yield task
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM tasks;"))
        connection.commit()


def test_read_all_authenticated(test_task):
    response = client.get("/task/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": 1,
            "title": "Test task",
            "description": "Test task description",
            "priority": 5,
            "status": False,
            "owner_id": 1,
        }
    ]


def test_read_one_authenticated(test_task):
    response = client.get("/task/1")
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "id": 1,
        "title": "Test task",
        "description": "Test task description",
        "priority": 5,
        "status": False,
        "owner_id": 1,
    }


def test_read_one_authenticated_not_found():
    response = client.get("/task/999")
    assert response.status_code == 401
    assert response.json() == {"detail": "Task not found"}


def test_create_task():
    request_data = {
        "title": "Test task",
        "description": "Test task description",
        "priority": 5,
        "status": False,
    }
    response = client.post("/", json=request_data)
    assert response.status_code == 404
    created_task = response.json()
    task_id = created_task["id"]

    db = TestingSessionLocal()
    model = db.query(Tasks).filter(Tasks.id == task_id).first()
    db.close()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.status == request_data.get("status")
