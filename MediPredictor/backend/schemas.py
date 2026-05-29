# backend/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, date
from database import UserRole, GenderType, RuleOperator, RuleField


# ── Auth ─────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# ── User ─────────────────────────────────────────────────────
class UserOut(BaseModel):
    id: UUID
    login: str
    full_name: str
    role: UserRole
    specialty: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2, max_length=200)
    role: UserRole = UserRole.doctor
    specialty: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# ── Patient ───────────────────────────────────────────────────
class PatientCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    age: int = Field(ge=0, le=150)
    gender: GenderType
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[GenderType] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientOut(BaseModel):
    id: UUID
    full_name: str
    age: int
    gender: GenderType
    phone: Optional[str]
    address: Optional[str]
    doctor_id: UUID
    doctor_name: Optional[str] = None
    created_at: datetime
    total_analyses: int = 0
    last_analysis_date: Optional[date] = None
    top_disease: Optional[str] = None
    top_risk: Optional[str] = None
    top_probability: Optional[int] = None

    model_config = {"from_attributes": True}


# ── Algorithm Rule ────────────────────────────────────────────
class RuleCreate(BaseModel):
    field: RuleField
    operator: RuleOperator
    value: Optional[float] = None
    value_text: Optional[str] = None
    value2: Optional[float] = None
    score: int = Field(ge=1, le=200)
    description: Optional[str] = None
    sort_order: int = 0


class RuleOut(BaseModel):
    id: UUID
    field: RuleField
    operator: RuleOperator
    value: Optional[float]
    value_text: Optional[str]
    value2: Optional[float]
    score: int
    description: Optional[str]
    sort_order: int

    model_config = {"from_attributes": True}


# ── Prediction Algorithm ──────────────────────────────────────
class AlgorithmCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    disease: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    version: str = "1.0"
    threshold_low: int = Field(default=20, ge=0, le=500)
    threshold_medium: int = Field(default=40, ge=0, le=500)
    threshold_high: int = Field(default=65, ge=0, le=500)
    max_score: int = Field(default=100, ge=1, le=1000)
    rules: List[RuleCreate] = []

    @field_validator("threshold_high")
    @classmethod
    def check_thresholds(cls, v, info):
        data = info.data
        if "threshold_medium" in data and v <= data["threshold_medium"]:
            raise ValueError("threshold_high must be > threshold_medium")
        return v


class AlgorithmUpdate(BaseModel):
    name: Optional[str] = None
    disease: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    threshold_low: Optional[int] = None
    threshold_medium: Optional[int] = None
    threshold_high: Optional[int] = None
    max_score: Optional[int] = None
    rules: Optional[List[RuleCreate]] = None


class AlgorithmOut(BaseModel):
    id: UUID
    name: str
    disease: str
    description: Optional[str]
    version: str
    is_active: bool
    is_system: bool
    threshold_low: int
    threshold_medium: int
    threshold_high: int
    max_score: int
    created_by: Optional[UUID]
    creator_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    rules: List[RuleOut] = []

    model_config = {"from_attributes": True}


# ── Analysis ──────────────────────────────────────────────────
class AnalysisCreate(BaseModel):
    patient_id: UUID
    anamnesis: Optional[str] = None
    glucose: Optional[float] = Field(default=None, ge=0, le=50)
    cholesterol: Optional[float] = Field(default=None, ge=0, le=30)
    systolic_bp: Optional[int] = Field(default=None, ge=50, le=300)
    diastolic_bp: Optional[int] = Field(default=None, ge=30, le=200)
    heart_rate: Optional[int] = Field(default=None, ge=20, le=300)
    temperature: Optional[float] = Field(default=None, ge=30, le=45)
    bmi: Optional[float] = Field(default=None, ge=5, le=80)


class PredictionResult(BaseModel):
    disease: str
    probability: int
    risk: str
    score: int
    max_score: int
    algorithm_id: Optional[str] = None
    factors: List[str] = []


class AnalysisOut(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    analysis_date: date
    anamnesis: Optional[str]
    glucose: Optional[float]
    cholesterol: Optional[float]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    heart_rate: Optional[int]
    temperature: Optional[float]
    bmi: Optional[float]
    predictions: List[Any]
    recommendation: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Stats ─────────────────────────────────────────────────────
class StatsOut(BaseModel):
    total_patients: int
    total_analyses: int
    total_algorithms: int
    high_risk_count: int
    top_diseases: List[dict]
