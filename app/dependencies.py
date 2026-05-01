from fastapi import Depends, HTTPException, Cookie, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import decode_token, get_user_by_username

def get_current_user(session_token: str = Cookie(default=None), db: Session = Depends(get_db)):
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(session_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = get_user_by_username(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
