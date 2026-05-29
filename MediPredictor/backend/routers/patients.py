# backend/routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from database import get_db, Patient, User, Analysis, UserRole
from auth import get_current_user, require_doctor_or_admin
from schemas import PatientOut, PatientCreate, PatientUpdate
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/api/patients", tags=["patients"])


async def _enrich(patient: Patient, db: AsyncSession) -> PatientOut:
    """Add computed fields to a patient."""
    # Count analyses
    cnt = await db.execute(
        select(func.count()).select_from(Analysis).where(Analysis.patient_id == patient.id)
    )
    total = cnt.scalar()

    # Last analysis
    last_res = await db.execute(
        select(Analysis)
        .where(Analysis.patient_id == patient.id)
        .order_by(Analysis.analysis_date.desc())
        .limit(1)
    )
    last: Analysis | None = last_res.scalar_one_or_none()

    # Doctor name
    doc_res = await db.execute(select(User).where(User.id == patient.doctor_id))
    doc = doc_res.scalar_one_or_none()

    top_disease = top_risk = None
    top_prob = None
    if last and last.predictions:
        top = last.predictions[0]
        top_disease = top.get("disease")
        top_risk = top.get("risk")
        top_prob = top.get("probability")

    out = PatientOut.model_validate(patient)
    out.total_analyses = total or 0
    out.last_analysis_date = last.analysis_date if last else None
    out.top_disease = top_disease
    out.top_risk = top_risk
    out.top_probability = top_prob
    out.doctor_name = doc.full_name if doc else None
    return out


@router.get("/", response_model=list[PatientOut])
async def list_patients(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    stmt = select(Patient)
    # Doctors see only their patients; admin/analyst see all
    if current.role == UserRole.doctor:
        stmt = stmt.where(Patient.doctor_id == current.id)
    if search:
        stmt = stmt.where(Patient.full_name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Patient.full_name)

    result = await db.execute(stmt)
    patients = result.scalars().all()
    return [await _enrich(p, db) for p in patients]


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    if current.role == UserRole.doctor and patient.doctor_id != current.id:
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    return await _enrich(patient, db)


@router.post("/", response_model=PatientOut, status_code=201)
async def create_patient(
    body: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    patient = Patient(**body.model_dump(), doctor_id=current.id)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return await _enrich(patient, db)


@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: UUID,
    body: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    if current.role == UserRole.doctor and patient.doctor_id != current.id:
        raise HTTPException(status_code=403, detail="Доступ заборонено")

    for k, v in body.model_dump(exclude_none=True).items():
        setattr(patient, k, v)
    await db.commit()
    await db.refresh(patient)
    return await _enrich(patient, db)


@router.delete("/{patient_id}", status_code=204)
async def delete_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    if current.role == UserRole.doctor and patient.doctor_id != current.id:
        raise HTTPException(status_code=403, detail="Доступ заборонено")
    await db.delete(patient)
    await db.commit()
