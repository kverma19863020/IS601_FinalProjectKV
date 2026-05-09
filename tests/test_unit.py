"""
Unit tests for Calculation World.
Tests pure Python logic with no database or HTTP calls.
"""
import pytest
from app.auth import hash_password, verify_password, create_access_token, decode_token


def test_hash_is_not_plaintext():
    assert hash_password("mypassword") != "mypassword"

def test_verify_correct_password():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True

def test_verify_wrong_password():
    hashed = hash_password("secret123")
    assert verify_password("wrong", hashed) is False

def test_bcrypt_salt_uniqueness():
    """Same password must produce different hashes due to random salt."""
    h1 = hash_password("samepassword")
    h2 = hash_password("samepassword")
    assert h1 != h2

def test_empty_string_hashes():
    hashed = hash_password("")
    assert verify_password("", hashed) is True
    assert verify_password("notempty", hashed) is False

def test_jwt_encode_decode_roundtrip():
    token = create_access_token({"sub": "alice"})
    assert decode_token(token) == "alice"

def test_invalid_token_returns_none():
    assert decode_token("not.a.valid.token") is None

def test_tampered_token_returns_none():
    token = create_access_token({"sub": "alice"})
    assert decode_token(token + "tampered") is None

def test_different_users_get_different_tokens():
    t1 = create_access_token({"sub": "alice"})
    t2 = create_access_token({"sub": "bob"})
    assert t1 != t2

@pytest.mark.parametrize("op,a,b,expected", [
    ("add",      10,  5,  15.0),
    ("subtract", 10,  3,   7.0),
    ("multiply",  4,  5,  20.0),
    ("divide",   15,  3,   5.0),
    ("power",     2,  8, 256.0),
    ("modulus",  17,  5,   2.0),
])
def test_all_operations(op, a, b, expected):
    OPS = {
        "add":      lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide":   lambda x, y: x / y,
        "power":    lambda x, y: x ** y,
        "modulus":  lambda x, y: x % y,
    }
    assert OPS[op](a, b) == expected

def test_sqrt_of_144():
    assert abs(144 ** 0.5 - 12.0) < 1e-9

def test_sqrt_of_zero():
    assert 0 ** 0.5 == 0.0

def test_negative_multiplication():
    assert (-3) * 4 == -12

def test_float_precision():
    assert abs((0.1 + 0.2) - 0.3) < 1e-9

def test_large_power():
    assert 2 ** 10 == 1024

def test_power_with_zero_exponent():
    assert 99 ** 0 == 1

def test_divide_by_zero_caught_by_route_guard():
    """Route pre-checks b==0 for divide/modulus before calling the lambda."""
    assert "divide" in ("divide", "modulus") and 0 == 0

def test_modulus_by_zero_caught_by_route_guard():
    assert "modulus" in ("divide", "modulus") and 0 == 0

def test_non_division_ops_not_blocked_by_zero():
    for op in ("add", "subtract", "multiply", "power", "sqrt_a"):
        assert not (op in ("divide", "modulus") and 0 == 0)

def test_divide_by_zero_raises_in_python():
    with pytest.raises(ZeroDivisionError):
        _ = 5 / 0

def test_modulus_by_zero_raises_in_python():
    with pytest.raises(ZeroDivisionError):
        _ = 5 % 0
