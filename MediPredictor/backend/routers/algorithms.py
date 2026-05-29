# backend/routers/algorithms.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db, PredictionAlgorithm, AlgorithmRule, User, UserRole
from auth import get_current_user, require_doctor_or_admin, require_admin
from schemas import AlgorithmOut, AlgorithmCreate, AlgorithmUpdate, RuleOut
from uuid import UUID

router = APIRouter(prefix="/api/algorithms", tags=["algorithms"])


def _algo_out(algo: PredictionAlgorithm, creator: User | None = None) -> AlgorithmOut:
    out = AlgorithmOut.model_validate(algo)
    out.creator_name = creator.full_name if creator else None
    out.rules = [RuleOut.model_validate(r) for r in algo.rules]
    return out


async def _load_algo(db: AsyncSession, algo_id: UUID) -> PredictionAlgorithm:
    result = await db.execute(
        select(PredictionAlgorithm)
        .where(PredictionAlgorithm.id == algo_id)
        .options(selectinload(PredictionAlgorithm.rules))
    )
    algo = result.scalar_one_or_none()
    if not algo:
        raise HTTPException(status_code=404, detail="Алгоритм не знайдено")
    return algo


@router.get("/", response_model=list[AlgorithmOut])
async def list_algorithms(
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """All users can view algorithms."""
    result = await db.execute(
        select(PredictionAlgorithm)
        .options(selectinload(PredictionAlgorithm.rules))
        .order_by(PredictionAlgorithm.disease)
    )
    algos = result.scalars().all()
    out = []
    for a in algos:
        creator = None
        if a.created_by:
            cr = await db.execute(select(User).where(User.id == a.created_by))
            creator = cr.scalar_one_or_none()
        out.append(_algo_out(a, creator))
    return out


@router.get("/{algo_id}", response_model=AlgorithmOut)
async def get_algorithm(
    algo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    algo = await _load_algo(db, algo_id)
    creator = None
    if algo.created_by:
        cr = await db.execute(select(User).where(User.id == algo.created_by))
        creator = cr.scalar_one_or_none()
    return _algo_out(algo, creator)


@router.post("/", response_model=AlgorithmOut, status_code=201)
async def create_algorithm(
    body: AlgorithmCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    """Doctors and admins can create algorithms."""
    algo = PredictionAlgorithm(
        name=body.name,
        disease=body.disease,
        description=body.description,
        version=body.version,
        threshold_low=body.threshold_low,
        threshold_medium=body.threshold_medium,
        threshold_high=body.threshold_high,
        max_score=body.max_score,
        created_by=current.id,
        is_system=False,
    )
    db.add(algo)
    await db.flush()  # get the ID

    for i, r in enumerate(body.rules):
        rule = AlgorithmRule(
            algorithm_id=algo.id,
            field=r.field,
            operator=r.operator,
            value=r.value,
            value_text=r.value_text,
            value2=r.value2,
            score=r.score,
            description=r.description,
            sort_order=r.sort_order if r.sort_order else i,
        )
        db.add(rule)

    await db.commit()

    # Reload with rules
    algo = await _load_algo(db, algo.id)
    return _algo_out(algo, current)


@router.put("/{algo_id}", response_model=AlgorithmOut)
async def update_algorithm(
    algo_id: UUID,
    body: AlgorithmUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    """
    Doctors can edit only their own non-system algorithms.
    Admins can edit any algorithm (including system ones).
    """
    algo = await _load_algo(db, algo_id)

    # Permission check
    if current.role == UserRole.doctor:
        if algo.is_system or algo.created_by != current.id:
            raise HTTPException(
                status_code=403,
                detail="Лікар може редагувати лише власні алгоритми"
            )

    # Update scalar fields
    for field_name in ("name", "disease", "description", "version", "is_active",
                        "threshold_low", "threshold_medium", "threshold_high", "max_score"):
        val = getattr(body, field_name, None)
        if val is not None:
            setattr(algo, field_name, val)

    # Replace rules if provided
    if body.rules is not None:
        # Delete existing rules
        for old_rule in list(algo.rules):
            await db.delete(old_rule)
        await db.flush()
        # Add new rules
        for i, r in enumerate(body.rules):
            rule = AlgorithmRule(
                algorithm_id=algo.id,
                field=r.field,
                operator=r.operator,
                value=r.value,
                value_text=r.value_text,
                value2=r.value2,
                score=r.score,
                description=r.description,
                sort_order=r.sort_order if r.sort_order else i,
            )
            db.add(rule)

    await db.commit()
    algo = await _load_algo(db, algo_id)
    creator = None
    if algo.created_by:
        cr = await db.execute(select(User).where(User.id == algo.created_by))
        creator = cr.scalar_one_or_none()
    return _algo_out(algo, creator)


@router.delete("/{algo_id}", status_code=204)
async def delete_algorithm(
    algo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    """
    Doctors can delete only their own non-system algorithms.
    Admins can delete any non-system algorithm.
    """
    algo = await _load_algo(db, algo_id)

    if algo.is_system:
        raise HTTPException(status_code=400, detail="Системний алгоритм не можна видалити")
    if current.role == UserRole.doctor and algo.created_by != current.id:
        raise HTTPException(status_code=403, detail="Доступ заборонено")

    await db.delete(algo)
    await db.commit()


@router.post("/{algo_id}/toggle", response_model=AlgorithmOut)
async def toggle_algorithm(
    algo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    """Enable / disable algorithm."""
    algo = await _load_algo(db, algo_id)
    if current.role == UserRole.doctor and algo.created_by != current.id and not algo.is_system:
        raise HTTPException(status_code=403)
    algo.is_active = not algo.is_active
    await db.commit()
    await db.refresh(algo)
    return _algo_out(algo, current)
