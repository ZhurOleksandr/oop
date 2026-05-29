# backend/routers/analyses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db, Analysis, Patient, User, PredictionAlgorithm, AlgorithmRule, UserRole
from auth import get_current_user, require_doctor_or_admin
from schemas import AnalysisOut, AnalysisCreate
from predictor import PatientData, run_algorithms
from uuid import UUID

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


@router.get("/patient/{patient_id}", response_model=list[AnalysisOut])
async def get_patient_analyses(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    # Verify access to patient
    pr = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = pr.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    if current.role == UserRole.doctor and patient.doctor_id != current.id:
        raise HTTPException(status_code=403)

    result = await db.execute(
        select(Analysis)
        .where(Analysis.patient_id == patient_id)
        .order_by(Analysis.analysis_date.desc(), Analysis.created_at.desc())
    )
    return [AnalysisOut.model_validate(a) for a in result.scalars()]


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Аналіз не знайдено")
    return AnalysisOut.model_validate(analysis)


@router.post("/", response_model=AnalysisOut, status_code=201)
async def create_analysis(
    body: AnalysisCreate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    # Verify patient
    pr = await db.execute(select(Patient).where(Patient.id == body.patient_id))
    patient = pr.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Пацієнта не знайдено")
    if current.role == UserRole.doctor and patient.doctor_id != current.id:
        raise HTTPException(status_code=403, detail="Доступ заборонено")

    # Load all active algorithms with rules
    algos_result = await db.execute(
        select(PredictionAlgorithm)
        .where(PredictionAlgorithm.is_active == True)
        .options(selectinload(PredictionAlgorithm.rules))
        .order_by(PredictionAlgorithm.disease)
    )
    algorithms = algos_result.scalars().all()

    # Build patient data object
    patient_data = PatientData(
        glucose=body.glucose,
        cholesterol=body.cholesterol,
        systolicBP=body.systolic_bp,
        diastolicBP=body.diastolic_bp,
        heart_rate=body.heart_rate,
        temperature=body.temperature,
        bmi=body.bmi,
        age=patient.age,
        gender=patient.gender.value,
        anamnesis=body.anamnesis or "",
    )

    # Run prediction engine
    predictions, recommendation = run_algorithms(algorithms, patient_data)

    # Save analysis
    analysis = Analysis(
        patient_id=body.patient_id,
        doctor_id=current.id,
        anamnesis=body.anamnesis,
        glucose=body.glucose,
        cholesterol=body.cholesterol,
        systolic_bp=body.systolic_bp,
        diastolic_bp=body.diastolic_bp,
        heart_rate=body.heart_rate,
        temperature=body.temperature,
        bmi=body.bmi,
        predictions=predictions,
        recommendation=recommendation,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return AnalysisOut.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=204)
async def delete_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_doctor_or_admin),
):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Аналіз не знайдено")
    if current.role == UserRole.doctor and analysis.doctor_id != current.id:
        raise HTTPException(status_code=403)
    await db.delete(analysis)
    await db.commit()
