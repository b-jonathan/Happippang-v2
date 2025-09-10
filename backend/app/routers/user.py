import os

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas import LoginRequest, RefreshToken, Token, UserCreate, UserOut
from app.services.auth import (
    authenticate_user,
    create_access_pair,
    get_current_user,
    hash_password,
    is_refresh_token_revoked,
    revoke_refresh_token,
    store_refresh_token,
)
from app.utils.db import get_session

ALGORITHM = os.getenv("ALGORITHM")
REFRESH_KEY = os.getenv("REFRESH_KEY")

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(User).where(User.username == user.username))
    if res.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    new_user = User(
        username=user.username,
        password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login(user: LoginRequest, db: AsyncSession = Depends(get_session)):
    auth_user = await authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    access_token, refresh_token = create_access_pair(user.username)
    await store_refresh_token(db, auth_user.id, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token_route(
    data: RefreshToken, db: AsyncSession = Depends(get_session)
):
    if await is_refresh_token_revoked(db, data.refresh_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    try:
        payload = jwt.decode(data.refresh_token, REFRESH_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    new_access, new_refresh = create_access_pair(username)

    user_res = await db.execute(select(User).where(User.username == username))
    user = user_res.scalar_one()

    await store_refresh_token(db, user.id, new_refresh)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(data: RefreshToken, db: AsyncSession = Depends(get_session)):
    await revoke_refresh_token(db, data.refresh_token)
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
