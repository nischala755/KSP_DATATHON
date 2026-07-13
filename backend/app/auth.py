from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User
from .seed import password_hash

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def create_token(user: User) -> str:
    payload = {"sub": str(user.id), "role": user.role, "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    return jwt.encode(payload, get_settings().jwt_secret, algorithm="HS256")


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username))
    return user if user and user.password_hash == password_hash(password) else None


def current_user(token: str | None = Depends(oauth2), db: Session = Depends(get_db)) -> User | None:
    if not token: return None
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
        return db.get(User, int(payload["sub"]))
    except Exception as exc:
        raise HTTPException(401, "Invalid or expired token") from exc

