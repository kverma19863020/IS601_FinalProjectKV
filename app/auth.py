"""
Authentication utilities for Calculation World (CLO13).
Implements bcrypt password hashing and JWT token auth.
Uses timezone-aware datetime to avoid Python 3.11+ deprecation warnings.
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY                  = os.getenv("SECRET_KEY", "changeme-use-a-long-random-string")
ALGORITHM                   = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """
    Return bcrypt hash of a plain-text password.
    bcrypt automatically salts each hash, protecting against rainbow table attacks.
    """
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Return True if the plain-text password matches the stored bcrypt hash.
    Uses constant-time comparison to prevent timing attacks.
    """
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    """
    Encode a signed JWT with an expiry claim.
    Uses timezone-aware UTC datetime (Python 3.11+ compatible).
    """
    payload        = data.copy()
    expire         = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Decode and validate a JWT token.
    Returns the 'sub' claim (username) or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
