# backend/routers/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db, Patient, Analysis, PredictionAlgorithm, User
from auth import get_current_user
from schemas import StatsOut
from collections import Counter

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/", response_model=StatsOut)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
):
    total_patients = (await db.execute(select(func.count()).select_from(Patient))).scalar()
    total_analyses = (await db.execute(select(func.count()).select_from(Analysis))).scalar()
    total_algorithms = (await db.execute(
        select(func.count()).select_from(PredictionAlgorithm).where(PredictionAlgorithm.is_active == True)
    )).scalar()

    # Gather all predictions for disease counting
    analyses_res = await db.execute(select(Analysis.predictions))
    all_predictions = analyses_res.scalars().all()

    disease_counter: Counter = Counter()
    high_risk_count = 0

    for preds in all_predictions:
        if not preds:
            continue
        for p in preds:
            if p.get("risk") == "high":
                disease_counter[p["disease"]] += 1
                high_risk_count += 1

    top_diseases = [
        {"disease": d, "count": c}
        for d, c in disease_counter.most_common(5)
    ]

    return StatsOut(
        total_patients=total_patients or 0,
        total_analyses=total_analyses or 0,
        total_algorithms=total_algorithms or 0,
        high_risk_count=high_risk_count,
        top_diseases=top_diseases,
    )
