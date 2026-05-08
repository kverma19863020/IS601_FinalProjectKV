"""
Integration tests for Calculation World.
Uses in-memory SQLite test database.
Covers all BREAD operations and auth flows.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base
from app import crud, schemas

# ── Test database ─────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_is601.db"
engine      = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Apply override globally once
app.dependency_overrides[get_db] = override_get_db


# ── Helpers ───────────────────────────────────────────────────

def make_client():
    """Return a fresh TestClient with cookie support."""
    return TestClient(app, raise_server_exceptions=True)


def logged_in_client(username="testplayer", password="pass1234"):
    """Return a TestClient that is already logged in."""
    c = make_client()
    r = c.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert r.status_code == 302, (
        f"Login failed: status={r.status_code} body={r.text[:200]}"
    )
    return c


# ── Session-scoped setup ──────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once, drop after all tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db_user():
    """Create the test user once for the whole session."""
    db   = TestSession()
    user = crud.get_user_by_username(db, "testplayer")
    if not user:
        user = crud.create_user(
            db,
            schemas.UserCreate(
                username="testplayer",
                email="test@calc.com",
                password="pass1234",
            ),
        )
    db.close()
    return user


# ── Auth tests ────────────────────────────────────────────────

def test_register_new_user():
    c = make_client()
    r = c.post(
        "/register",
        data={
            "username": "brandnewuser",
            "email":    "brandnew@test.com",
            "password": "pass1234",
        },
        follow_redirects=False,
    )
    assert r.status_code in (200, 302)


def test_register_duplicate_username(db_user):
    c = make_client()
    r = c.post(
        "/register",
        data={
            "username": "testplayer",
            "email":    "other@test.com",
            "password": "pass1234",
        },
        follow_redirects=True,
    )
    assert r.status_code == 400
    assert b"already" in r.content.lower()


def test_login_valid(db_user):
    c = make_client()
    r = c.post(
        "/login",
        data={"username": "testplayer", "password": "pass1234"},
        follow_redirects=False,
    )
    assert r.status_code == 302


def test_login_invalid_password(db_user):
    c = make_client()
    r = c.post(
        "/login",
        data={"username": "testplayer", "password": "wrongpass"},
        follow_redirects=True,
    )
    assert r.status_code == 400


def test_logout(db_user):
    c = logged_in_client()
    r = c.get("/logout", follow_redirects=False)
    assert r.status_code == 302


# ── Dashboard ─────────────────────────────────────────────────

def test_dashboard_unauthenticated():
    c = make_client()
    r = c.get("/dashboard", follow_redirects=False)
    assert r.status_code == 302


def test_dashboard_authenticated(db_user):
    c = logged_in_client()
    r = c.get("/dashboard")
    assert r.status_code == 200


# ── BREAD: Add ────────────────────────────────────────────────

def test_calculate_addition(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "10", "b": "5", "operation": "add"})
    assert r.status_code == 200
    assert b"15" in r.content


def test_calculate_subtraction(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "10", "b": "3", "operation": "subtract"})
    assert r.status_code == 200
    assert b"7" in r.content


def test_calculate_multiplication(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "4", "b": "5", "operation": "multiply"})
    assert r.status_code == 200
    assert b"20" in r.content


def test_calculate_division(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "15", "b": "3", "operation": "divide"})
    assert r.status_code == 200
    assert b"5" in r.content


def test_calculate_power(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "2", "b": "8", "operation": "power"})
    assert r.status_code == 200
    assert b"256" in r.content


def test_calculate_modulus(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "17", "b": "5", "operation": "modulus"})
    assert r.status_code == 200
    assert b"2" in r.content


def test_calculate_sqrt(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "144", "b": "0", "operation": "sqrt_a"})
    assert r.status_code == 200
    assert b"12" in r.content


def test_calculate_divide_by_zero(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "10", "b": "0", "operation": "divide"})
    assert r.status_code == 200
    assert b"zero" in r.content.lower()


def test_calculate_modulus_by_zero(db_user):
    c = logged_in_client()
    r = c.post("/calculate", data={"a": "10", "b": "0", "operation": "modulus"})
    assert r.status_code == 200
    assert b"zero" in r.content.lower()


# ── BREAD: Browse ─────────────────────────────────────────────

def test_history_page_loads(db_user):
    c = logged_in_client()
    r = c.get("/history")
    assert r.status_code == 200


def test_history_unauthenticated():
    c = make_client()
    r = c.get("/history", follow_redirects=False)
    assert r.status_code == 302


# ── BREAD: Read ───────────────────────────────────────────────

def test_read_calculation(db_user):
    db   = TestSession()
    calc = crud.get_history(db, db_user.id, limit=1)
    db.close()
    if calc:
        c = logged_in_client()
        r = c.get(f"/calculation/{calc[0].id}")
        assert r.status_code == 200


# ── BREAD: Edit ───────────────────────────────────────────────

def test_edit_calculation(db_user):
    db   = TestSession()
    calc = crud.get_history(db, db_user.id, limit=1)
    db.close()
    if calc:
        c = logged_in_client()
        r = c.post(
            f"/calculation/{calc[0].id}/edit",
            data={"a": "99", "b": "1", "operation": "add"},
            follow_redirects=False,
        )
        assert r.status_code == 302


# ── BREAD: Delete ─────────────────────────────────────────────

def test_delete_calculation(db_user):
    db = TestSession()
    new_calc = crud.create_calculation(
        db,
        schemas.CalculationCreate(
            user_id=db_user.id,
            operand_a=1,
            operand_b=1,
            operation="add",
            result=2,
        ),
    )
    calc_id = new_calc.id
    db.close()

    c = logged_in_client()
    r = c.post(f"/calculation/{calc_id}/delete", follow_redirects=False)
    assert r.status_code == 302


# ── Export ────────────────────────────────────────────────────

def test_export_csv(db_user):
    c = logged_in_client()
    r = c.get("/history/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")


def test_export_excel(db_user):
    c = logged_in_client()
    r = c.get("/history/export/excel")
    assert r.status_code == 200
    assert "spreadsheetml" in r.headers.get("content-type", "")


# ── Forgot username ───────────────────────────────────────────

def test_forgot_username_found(db_user):
    c = make_client()
    r = c.post("/forgot-username", data={"email": "test@calc.com"})
    assert r.status_code == 200
    assert b"testplayer" in r.content


def test_forgot_username_not_found():
    c = make_client()
    r = c.post("/forgot-username", data={"email": "nobody@nowhere.com"})
    assert r.status_code == 200
    assert b"No account" in r.content


# ── Reset password ────────────────────────────────────────────

def test_reset_password_success(db_user):
    c = make_client()
    r = c.post(
        "/reset-password",
        data={"email": "test@calc.com", "new_password": "pass1234"},
    )
    assert r.status_code == 200
    assert b"updated" in r.content.lower()


def test_reset_password_bad_email():
    c = make_client()
    r = c.post(
        "/reset-password",
        data={"email": "nobody@x.com", "new_password": "xyz"},
    )
    assert r.status_code == 200
    assert b"No account" in r.content


# ── Profile ───────────────────────────────────────────────────

def test_profile_page_loads(db_user):
    c = logged_in_client()
    r = c.get("/profile")
    assert r.status_code == 200


def test_profile_wrong_password(db_user):
    c = logged_in_client()
    r = c.post(
        "/profile",
        data={
            "email":            "x@x.com",
            "current_password": "wrongone",
            "new_password":     "",
        },
    )
    assert r.status_code == 200
    assert b"incorrect" in r.content.lower()


# ── REST API ──────────────────────────────────────────────────

def test_api_calculate(db_user):
    c = logged_in_client()
    r = c.post(
        "/api/calculate",
        json={"operand_a": 9, "operand_b": 3, "operation": "divide"},
    )
    assert r.status_code == 200
    assert r.json()["result"] == 3.0


def test_api_history_returns_list(db_user):
    c = logged_in_client()
    r = c.get("/api/history")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_api_unauthenticated():
    c = make_client()
    r = c.get("/api/history")
    assert r.status_code == 401


def test_api_divide_by_zero(db_user):
    c = logged_in_client()
    r = c.post(
        "/api/calculate",
        json={"operand_a": 10, "operand_b": 0, "operation": "divide"},
    )
    assert r.status_code == 400
    assert "zero" in r.json()["detail"].lower()


def test_api_delete(db_user):
    db = TestSession()
    calc = crud.create_calculation(
        db,
        schemas.CalculationCreate(
            user_id=db_user.id,
            operand_a=5,
            operand_b=5,
            operation="add",
            result=10,
        ),
    )
    calc_id = calc.id
    db.close()

    c = logged_in_client()
    r = c.delete(f"/api/calculation/{calc_id}")
    assert r.status_code == 200
    assert r.json()["message"] == "Deleted successfully"
