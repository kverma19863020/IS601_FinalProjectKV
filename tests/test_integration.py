import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app import crud, schemas

TEST_DB = "sqlite:///./test_is601.db"
engine  = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    db = TestSession()
    user = crud.get_user_by_username(db, "testplayer")
    if not user:
        user = crud.create_user(db, schemas.UserCreate(
            username="testplayer", email="test@calc.com", password="pass1234"
        ))
    db.close()
    return user


@pytest.fixture
def auth_client(client, test_user):
    client.post("/login", data={"username": "testplayer", "password": "pass1234"}, follow_redirects=False)
    return client


def test_register_new_user(client):
    r = client.post("/register", data={"username": "newuser99", "email": "new99@test.com", "password": "pass1234"}, follow_redirects=False)
    assert r.status_code in (200, 302)


def test_register_duplicate_username(client, test_user):
    r = client.post("/register", data={"username": "testplayer", "email": "other@test.com", "password": "pass1234"})
    assert b"already" in r.content.lower()


def test_login_valid(client, test_user):
    r = client.post("/login", data={"username": "testplayer", "password": "pass1234"}, follow_redirects=False)
    assert r.status_code == 302


def test_login_invalid_password(client, test_user):
    r = client.post("/login", data={"username": "testplayer", "password": "wrongpass"})
    assert r.status_code == 400


def test_dashboard_unauthenticated(client):
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 302


def test_dashboard_authenticated(auth_client):
    r = auth_client.get("/dashboard")
    assert r.status_code == 200


def test_calculator_page(auth_client):
    r = auth_client.get("/calculator")
    assert r.status_code == 200


def test_calculate_addition(auth_client):
    r = auth_client.post("/calculate", data={"a": "10", "b": "5", "operation": "add"})
    assert r.status_code == 200
    assert b"15" in r.content


def test_calculate_power(auth_client):
    r = auth_client.post("/calculate", data={"a": "2", "b": "8", "operation": "power"})
    assert r.status_code == 200
    assert b"256" in r.content


def test_calculate_divide_by_zero(auth_client):
    r = auth_client.post("/calculate", data={"a": "10", "b": "0", "operation": "divide"})
    assert r.status_code == 200
    assert b"zero" in r.content.lower()


def test_calculate_modulus(auth_client):
    r = auth_client.post("/calculate", data={"a": "17", "b": "5", "operation": "modulus"})
    assert r.status_code == 200
    assert b"2" in r.content


def test_calculate_sqrt(auth_client):
    r = auth_client.post("/calculate", data={"a": "144", "b": "0", "operation": "sqrt_a"})
    assert r.status_code == 200
    assert b"12" in r.content


def test_history_page(auth_client):
    r = auth_client.get("/history")
    assert r.status_code == 200


def test_history_unauthenticated(client):
    r = client.get("/history", follow_redirects=False)
    assert r.status_code == 302


def test_export_csv(auth_client):
    r = auth_client.get("/history/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")


def test_forgot_username_found(client, test_user):
    r = client.post("/forgot-username", data={"email": "test@calc.com"})
    assert b"testplayer" in r.content


def test_forgot_username_not_found(client):
    r = client.post("/forgot-username", data={"email": "nobody@nowhere.com"})
    assert b"No account" in r.content


def test_reset_password_success(client, test_user):
    r = client.post("/reset-password", data={"email": "test@calc.com", "new_password": "newpass99"})
    assert b"updated" in r.content.lower()


def test_reset_password_bad_email(client):
    r = client.post("/reset-password", data={"email": "nobody@x.com", "new_password": "xyz"})
    assert b"No account" in r.content


def test_profile_page(auth_client):
    r = auth_client.get("/profile")
    assert r.status_code == 200


def test_profile_wrong_password(auth_client):
    r = auth_client.post("/profile", data={"email": "x@x.com", "current_password": "wrongone", "new_password": ""})
    assert b"incorrect" in r.content.lower()


def test_api_calculate(auth_client):
    r = auth_client.post("/api/calculate", json={"operand_a": 9, "operand_b": 3, "operation": "divide"})
    assert r.status_code == 200
    assert r.json()["result"] == 3.0


def test_api_history(auth_client):
    r = auth_client.get("/api/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_api_unauthenticated(client):
    r = client.get("/api/history")
    assert r.status_code == 401
