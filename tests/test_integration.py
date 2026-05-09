"""
Integration tests for Calculation World.
Tests all FastAPI routes against an in-memory SQLite test database.
Each test uses a fresh logged-in client to avoid cookie leakage.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app import crud, schemas

TEST_DB_URL = "sqlite:///./test_calcworld.db"
engine      = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def make_client():
    return TestClient(app, raise_server_exceptions=True)


def logged_in_client(username="testplayer", password="pass1234"):
    client = make_client()
    resp   = client.post("/login", data={"username": username, "password": password}, follow_redirects=False)
    assert resp.status_code == 302, f"Login failed: {resp.status_code} {resp.text[:200]}"
    return client


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_user():
    db   = TestSession()
    user = crud.get_user_by_username(db, "testplayer")
    if not user:
        user = crud.create_user(db, schemas.UserCreate(username="testplayer", email="test@calcworld.com", password="pass1234"))
    db.close()
    return user


def test_register_new_user():
    r = make_client().post("/register", data={"username": "freshuser1", "email": "fresh1@test.com", "password": "pass1234"}, follow_redirects=False)
    assert r.status_code in (200, 302)

def test_register_duplicate_username(db_user):
    r = make_client().post("/register", data={"username": "testplayer", "email": "other@test.com", "password": "pass1234"}, follow_redirects=True)
    assert r.status_code == 400
    assert b"already" in r.content.lower()

def test_register_duplicate_email(db_user):
    r = make_client().post("/register", data={"username": "newuser99", "email": "test@calcworld.com", "password": "pass1234"}, follow_redirects=True)
    assert r.status_code == 400

def test_login_valid(db_user):
    r = make_client().post("/login", data={"username": "testplayer", "password": "pass1234"}, follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "/dashboard"

def test_login_wrong_password(db_user):
    r = make_client().post("/login", data={"username": "testplayer", "password": "bad"}, follow_redirects=True)
    assert r.status_code == 400

def test_login_nonexistent_user():
    r = make_client().post("/login", data={"username": "ghost", "password": "x"}, follow_redirects=True)
    assert r.status_code == 400

def test_logout(db_user):
    r = logged_in_client().get("/logout", follow_redirects=False)
    assert r.status_code == 302

def test_dashboard_unauthenticated():
    r = make_client().get("/dashboard", follow_redirects=False)
    assert r.status_code == 302

def test_dashboard_authenticated(db_user):
    r = logged_in_client().get("/dashboard")
    assert r.status_code == 200

def test_calculate_addition(db_user):
    r = logged_in_client().post("/calculate", data={"a": "10", "b": "5", "operation": "add"})
    assert r.status_code == 200
    assert b"15" in r.content

def test_calculate_subtraction(db_user):
    r = logged_in_client().post("/calculate", data={"a": "10", "b": "3", "operation": "subtract"})
    assert r.status_code == 200
    assert b"7" in r.content

def test_calculate_multiplication(db_user):
    r = logged_in_client().post("/calculate", data={"a": "6", "b": "7", "operation": "multiply"})
    assert r.status_code == 200
    assert b"42" in r.content

def test_calculate_division(db_user):
    r = logged_in_client().post("/calculate", data={"a": "15", "b": "3", "operation": "divide"})
    assert r.status_code == 200
    assert b"5" in r.content

def test_calculate_power(db_user):
    r = logged_in_client().post("/calculate", data={"a": "2", "b": "8", "operation": "power"})
    assert r.status_code == 200
    assert b"256" in r.content

def test_calculate_modulus(db_user):
    r = logged_in_client().post("/calculate", data={"a": "17", "b": "5", "operation": "modulus"})
    assert r.status_code == 200
    assert b"2" in r.content

def test_calculate_sqrt(db_user):
    r = logged_in_client().post("/calculate", data={"a": "144", "b": "0", "operation": "sqrt_a"})
    assert r.status_code == 200
    assert b"12" in r.content

def test_calculate_divide_by_zero(db_user):
    r = logged_in_client().post("/calculate", data={"a": "10", "b": "0", "operation": "divide"})
    assert r.status_code == 200
    assert b"zero" in r.content.lower()

def test_calculate_modulus_by_zero(db_user):
    r = logged_in_client().post("/calculate", data={"a": "10", "b": "0", "operation": "modulus"})
    assert r.status_code == 200
    assert b"zero" in r.content.lower()

def test_calculate_unauthenticated():
    r = make_client().post("/calculate", data={"a": "1", "b": "1", "operation": "add"}, follow_redirects=False)
    assert r.status_code == 302

def test_history_page_loads(db_user):
    r = logged_in_client().get("/history")
    assert r.status_code == 200

def test_history_unauthenticated():
    r = make_client().get("/history", follow_redirects=False)
    assert r.status_code == 302

def test_read_calculation(db_user):
    db = TestSession()
    calc = crud.get_history(db, db_user.id, limit=1)
    db.close()
    if calc:
        r = logged_in_client().get(f"/calculation/{calc[0].id}")
        assert r.status_code == 200

def test_read_nonexistent_calculation(db_user):
    r = logged_in_client().get("/calculation/999999")
    assert r.status_code == 404

def test_edit_calculation(db_user):
    db = TestSession()
    calc = crud.get_history(db, db_user.id, limit=1)
    db.close()
    if calc:
        r = logged_in_client().post(f"/calculation/{calc[0].id}/edit", data={"a": "99", "b": "1", "operation": "add"}, follow_redirects=False)
        assert r.status_code == 302

def test_edit_calculation_divide_by_zero(db_user):
    db = TestSession()
    calc = crud.get_history(db, db_user.id, limit=1)
    db.close()
    if calc:
        r = logged_in_client().post(f"/calculation/{calc[0].id}/edit", data={"a": "10", "b": "0", "operation": "divide"})
        assert r.status_code == 200
        assert b"zero" in r.content.lower()

def test_delete_calculation(db_user):
    db = TestSession()
    new_calc = crud.create_calculation(db, schemas.CalculationCreate(user_id=db_user.id, operand_a=1, operand_b=1, operation="add", result=2))
    calc_id = new_calc.id
    db.close()
    r = logged_in_client().post(f"/calculation/{calc_id}/delete", follow_redirects=False)
    assert r.status_code == 302

def test_export_csv(db_user):
    r = logged_in_client().get("/history/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")

def test_export_excel(db_user):
    r = logged_in_client().get("/history/export/excel")
    assert r.status_code == 200
    assert "spreadsheetml" in r.headers.get("content-type", "")

def test_export_pdf(db_user):
    r = logged_in_client().get("/history/export/pdf")
    assert r.status_code == 200
    assert "pdf" in r.headers.get("content-type", "")

def test_forgot_username_found(db_user):
    r = make_client().post("/forgot-username", data={"email": "test@calcworld.com"})
    assert r.status_code == 200
    assert b"testplayer" in r.content

def test_forgot_username_not_found():
    r = make_client().post("/forgot-username", data={"email": "nobody@x.com"})
    assert r.status_code == 200
    assert b"No account" in r.content

def test_reset_password_success(db_user):
    r = make_client().post("/reset-password", data={"email": "test@calcworld.com", "new_password": "pass1234"})
    assert r.status_code == 200
    assert b"updated" in r.content.lower()

def test_reset_password_bad_email():
    r = make_client().post("/reset-password", data={"email": "nobody@x.com", "new_password": "xyz"})
    assert r.status_code == 200
    assert b"No account" in r.content

def test_profile_page_loads(db_user):
    r = logged_in_client().get("/profile")
    assert r.status_code == 200

def test_profile_wrong_current_password(db_user):
    r = logged_in_client().post("/profile", data={"email": "x@x.com", "current_password": "wrongpassword", "new_password": ""})
    assert r.status_code == 200
    assert b"incorrect" in r.content.lower()

def test_profile_unauthenticated():
    r = make_client().get("/profile", follow_redirects=False)
    assert r.status_code == 302

def test_api_calculate(db_user):
    r = logged_in_client().post("/api/calculate", json={"operand_a": 9, "operand_b": 3, "operation": "divide"})
    assert r.status_code == 200
    assert r.json()["result"] == 3.0

def test_api_calculate_power(db_user):
    r = logged_in_client().post("/api/calculate", json={"operand_a": 2, "operand_b": 10, "operation": "power"})
    assert r.status_code == 200
    assert r.json()["result"] == 1024.0

def test_api_history_returns_list(db_user):
    r = logged_in_client().get("/api/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0

def test_api_history_unauthenticated():
    r = make_client().get("/api/history")
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"

def test_api_divide_by_zero(db_user):
    r = logged_in_client().post("/api/calculate", json={"operand_a": 10, "operand_b": 0, "operation": "divide"})
    assert r.status_code == 400
    assert "zero" in r.json()["detail"].lower()

def test_api_modulus_by_zero(db_user):
    r = logged_in_client().post("/api/calculate", json={"operand_a": 10, "operand_b": 0, "operation": "modulus"})
    assert r.status_code == 400

def test_api_unknown_operation(db_user):
    r = logged_in_client().post("/api/calculate", json={"operand_a": 1, "operand_b": 1, "operation": "invalid_op"})
    assert r.status_code == 400

def test_api_delete_calculation(db_user):
    db = TestSession()
    calc = crud.create_calculation(db, schemas.CalculationCreate(user_id=db_user.id, operand_a=5, operand_b=5, operation="add", result=10))
    calc_id = calc.id
    db.close()
    r = logged_in_client().delete(f"/api/calculation/{calc_id}")
    assert r.status_code == 200
    assert r.json()["message"] == "Deleted successfully"

def test_api_delete_unauthenticated():
    r = make_client().delete("/api/calculation/1")
    assert r.status_code == 401
