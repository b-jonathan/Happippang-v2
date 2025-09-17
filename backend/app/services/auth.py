import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.appmodels import Token, User
from backend.apputils.db import get_session

SECRET_KEY = os.getenv("HASH_KEY")  # Change this!
REFRESH_KEY = os.getenv("REFRESH_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, REFRESH_KEY, algorithm=ALGORITHM)


def create_access_pair(username: str):
    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)
    return (access_token, refresh_token)


def refresh_access_pair(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, REFRESH_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_access, new_refresh = create_access_pair(username)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


async def store_refresh_token(db: AsyncSession, user_id: str, token: str):
    row = Token(user_id=user_id, token=token)
    db.add(row)
    await db.commit()


async def revoke_refresh_token(db: AsyncSession, token: str):
    res = await db.execute(select(Token).where(Token.token == token))
    row = res.scalar_one_or_none()
    if row:
        row.revoked = True
        await db.commit()


async def is_refresh_token_revoked(db: AsyncSession, token: str) -> bool:
    res = await db.execute(select(Token).where(Token.token == token))
    row = res.scalar_one_or_none()
    return row.revoked if row else True  # treat unknown as revoked


async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password):
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user
