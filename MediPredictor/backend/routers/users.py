# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db, User
from auth import hash_password, require_admin, get_current_user
from schemas import UserOut, UserCreate, UserUpdate
from uuid import UUID

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.full_name))
    return [UserOut.model_validate(u) for u in result.scalars()]


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    exists = await db.execute(select(User).where(User.login == body.login))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Логін вже зайнятий")

    user = User(
        login=body.login,
        password=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        specialty=body.specialty,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.role is not None:
        user.role = body.role
    if body.specialty is not None:
        user.specialty = body.specialty
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password:
        user.password = hash_password(body.password)

    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_admin),
):
    if current.id == user_id:
        raise HTTPException(status_code=400, detail="Не можна видалити власний акаунт")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    await db.delete(user)
    await db.commit()
