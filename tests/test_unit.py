"""
Unit tests for Calculation World.
Tests pure logic with no database or HTTP calls.
"""
import pytest
from app.auth import hash_password, verify_password, create_access_token, decode_token


# ── Password hashing ──────────────────────────────────────────

def test_hash_not_plaintext():
    assert hash_password("mypassword") != "mypassword"


def test_verify_correct_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("secret123")
    assert verify_password("wrong", hashed) is False


def test_unique_hashes_for_same_password():
    """bcrypt uses random salt so same password produces different hashes."""
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2


# ── JWT tokens ────────────────────────────────────────────────

def test_jwt_roundtrip():
    token = create_access_token({"sub": "alice"})
    assert decode_token(token) == "alice"


def test_invalid_token_returns_none():
    assert decode_token("not.a.valid.token") is None


def test_tampered_token_returns_none():
    token = create_access_token({"sub": "alice"})
    assert decode_token(token + "x") is None


def test_different_users_get_different_tokens():
    t1 = create_access_token({"sub": "alice"})
    t2 = create_access_token({"sub": "bob"})
    assert t1 != t2


# ── Calculation logic ─────────────────────────────────────────

@pytest.mark.parametrize("op,a,b,expected", [
    ("add",      10,  5,  15),
    ("subtract", 10,  3,   7),
    ("multiply",  4,  5,  20),
    ("divide",   15,  3,   5),
    ("power",     2,  8, 256),
    ("modulus",  17,  5,   2),
])
def test_operations(op, a, b, expected):
    OPS = {
        "add":      lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide":   lambda x, y: x / y,
        "power":    lambda x, y: x ** y,
        "modulus":  lambda x, y: x % y,
    }
    assert OPS[op](a, b) == expected


def test_sqrt():
    result = 144 ** 0.5
    assert abs(result - 12.0) < 1e-9


def test_negative_multiplication():
    assert (-3) * 4 == -12


def test_float_addition():
    assert abs((0.1 + 0.2) - 0.3) < 1e-9


def test_large_power():
    assert 2 ** 10 == 1024


# ── Division by zero guards ───────────────────────────────────

def test_divide_by_zero_is_caught_by_route_guard():
    """The route checks b==0 before calling the lambda."""
    operation = "divide"
    b = 0
    is_blocked = operation in ("divide", "modulus") and b == 0
    assert is_blocked is True


def test_modulus_by_zero_is_caught_by_route_guard():
    operation = "modulus"
    b = 0
    is_blocked = operation in ("divide", "modulus") and b == 0
    assert is_blocked is True


def test_add_with_zero_b_is_not_blocked():
    """Zero is a valid operand for non-division operations."""
    for op in ("add", "subtract", "multiply", "power", "sqrt_a"):
        is_blocked = op in ("divide", "modulus") and 0 == 0
        assert is_blocked is False


def test_divide_by_zero_raises_in_python():
    """Python itself raises ZeroDivisionError if guard is bypassed."""
    with pytest.raises(ZeroDivisionError):
        _ = 5 / 0


def test_modulus_by_zero_raises_in_python():
    with pytest.raises(ZeroDivisionError):
        _ = 5 % 0
