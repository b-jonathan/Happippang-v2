import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Token, User
from backend.app.utils.db import get_session

# ---------------------- Logging setup ----------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("auth")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)


def _mask_token(tok: Optional[str]) -> str:
    if not tok:
        return "<none>"
    return f"{tok[:8]}…{tok[-6:]}(len={len(tok)})"


# -----------------------------------------------------------

SECRET_KEY = os.getenv("HASH_KEY")
REFRESH_KEY = os.getenv("REFRESH_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    # never log raw password
    logger.debug("hash_password called")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug("verify_password called")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(
        "create_access_token",
        extra={
            "username": username,
            "exp": expire.isoformat(),
            "alg": ALGORITHM,
            "token_preview": _mask_token(token),
        },
    )
    return token


def create_refresh_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, REFRESH_KEY, algorithm=ALGORITHM)
    logger.debug(
        "create_refresh_token",
        extra={
            "username": username,
            "exp": expire.isoformat(),
            "alg": ALGORITHM,
            "token_preview": _mask_token(token),
        },
    )
    return token


def create_access_pair(username: str):
    logger.info("creating token pair", extra={"username": username})
    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)
    return (access_token, refresh_token)


def refresh_access_pair(refresh_token: str) -> dict:
    logger.info(
        "refresh_access_pair called", extra={"rt_preview": _mask_token(refresh_token)}
    )
    try:
        payload = jwt.decode(refresh_token, REFRESH_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("refresh token missing sub")
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except JWTError as e:
        logger.warning("refresh token decode failed", extra={"error": repr(e)})
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_access, new_refresh = create_access_pair(username)
    logger.info(
        "issued new token pair",
        extra={
            "username": username,
            "at_preview": _mask_token(new_access),
            "rt_preview": _mask_token(new_refresh),
        },
    )
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


async def store_refresh_token(db: AsyncSession, user_id: str, token: str):
    logger.info(
        "store_refresh_token",
        extra={"user_id": str(user_id), "rt_preview": _mask_token(token)},
    )
    row = Token(user_id=user_id, token=token)
    db.add(row)
    await db.commit()


async def revoke_refresh_token(db: AsyncSession, token: str):
    logger.info("revoke_refresh_token", extra={"rt_preview": _mask_token(token)})
    res = await db.execute(select(Token).where(Token.token == token))
    row = res.scalar_one_or_none()
    if row:
        row.revoked = True
        await db.commit()
        logger.info("refresh token revoked")
    else:
        logger.info("refresh token not found; nothing to revoke")


async def is_refresh_token_revoked(db: AsyncSession, token: str) -> bool:
    logger.debug("is_refresh_token_revoked", extra={"rt_preview": _mask_token(token)})
    res = await db.execute(select(Token).where(Token.token == token))
    row = res.scalar_one_or_none()
    revoked = row.revoked if row else True
    logger.debug("revocation check result", extra={"revoked": revoked})
    return revoked


async def authenticate_user(db: AsyncSession, username: str, password: str):
    logger.info("authenticate_user start", extra={"username": username})
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning("user not found", extra={"username": username})
            return None
        ok = verify_password(password, user.password)
        if not ok:
            logger.warning("password verify failed", extra={"username": username})
            return None
        logger.info(
            "authenticate_user success",
            extra={"username": username, "user_id": str(user.id)},
        )
        return user
    except Exception as e:
        logger.error(
            "authenticate_user exception",
            extra={"username": username, "error": repr(e)},
        )
        raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_session),
):
    token = credentials.credentials
    logger.debug("get_current_user called", extra={"at_preview": _mask_token(token)})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            logger.warning("token missing sub")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    except JWTError as e:
        logger.warning("token decode failed", extra={"error": repr(e)})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning("user not found for token", extra={"username": username})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    logger.debug(
        "get_current_user success",
        extra={"username": username, "user_id": str(user.id)},
    )
    return user
