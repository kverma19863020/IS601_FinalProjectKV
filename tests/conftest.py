import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    def override():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override
    with TestClient(app, follow_redirects=True) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client):
    client.post("/register", data={"username": "testuser", "email": "t@t.com", "password": "pass123"})
    client.post("/login", data={"username": "testuser", "password": "pass123"})
    return client
