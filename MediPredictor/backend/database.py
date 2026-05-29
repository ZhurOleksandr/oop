# backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Boolean, SmallInteger, Numeric, Text, Date,
    ForeignKey, Enum as SAEnum, TIMESTAMP, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
import enum
from datetime import datetime, date
from config import get_settings

settings = get_settings()

# Використовуємо db_url property — автоматично обирає між DB_* змінними і DATABASE_URL
engine = create_async_engine(
    settings.db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass


# ── Enums ─────────────────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    doctor   = "doctor"
    admin    = "admin"
    analyst  = "analyst"


class GenderType(str, enum.Enum):
    male   = "male"
    female = "female"


class RuleOperator(str, enum.Enum):
    gt          = "gt"
    gte         = "gte"
    lt          = "lt"
    lte         = "lte"
    eq          = "eq"
    between     = "between"
    contains    = "contains"
    not_contains = "not_contains"


class RuleField(str, enum.Enum):
    glucose     = "glucose"
    cholesterol = "cholesterol"
    systolicBP  = "systolicBP"
    diastolicBP = "diastolicBP"
    age         = "age"
    gender      = "gender"
    anamnesis   = "anamnesis"
    bmi         = "bmi"
    heartRate   = "heartRate"
    temperature = "temperature"


# ── ORM Models ────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id:         Mapped[uuid.UUID]      = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login:      Mapped[str]            = mapped_column(String(64), unique=True, nullable=False)
    password:   Mapped[str]            = mapped_column(String(128), nullable=False)
    full_name:  Mapped[str]            = mapped_column(String(200), nullable=False)
    role:       Mapped[UserRole]       = mapped_column(SAEnum(UserRole), default=UserRole.doctor)
    specialty:  Mapped[str | None]     = mapped_column(String(100))
    is_active:  Mapped[bool]           = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]       = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime]       = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    patients:   Mapped[list["Patient"]]             = relationship(back_populates="doctor")
    algorithms: Mapped[list["PredictionAlgorithm"]] = relationship(back_populates="creator")


class Patient(Base):
    __tablename__ = "patients"

    id:         Mapped[uuid.UUID]  = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name:  Mapped[str]        = mapped_column(String(200), nullable=False)
    age:        Mapped[int]        = mapped_column(SmallInteger, nullable=False)
    gender:     Mapped[GenderType] = mapped_column(SAEnum(GenderType), nullable=False)
    phone:      Mapped[str | None] = mapped_column(String(20))
    address:    Mapped[str | None] = mapped_column(Text)
    doctor_id:  Mapped[uuid.UUID]  = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime]   = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime]   = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    doctor:   Mapped["User"]         = relationship(back_populates="patients")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="patient", cascade="all, delete")


class PredictionAlgorithm(Base):
    __tablename__ = "prediction_algorithms"

    id:               Mapped[uuid.UUID]    = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name:             Mapped[str]          = mapped_column(String(200), nullable=False)
    disease:          Mapped[str]          = mapped_column(String(200), nullable=False)
    description:      Mapped[str | None]   = mapped_column(Text)
    version:          Mapped[str]          = mapped_column(String(20), default="1.0")
    is_active:        Mapped[bool]         = mapped_column(Boolean, default=True)
    is_system:        Mapped[bool]         = mapped_column(Boolean, default=False)
    threshold_low:    Mapped[int]          = mapped_column(SmallInteger, default=20)
    threshold_medium: Mapped[int]          = mapped_column(SmallInteger, default=40)
    threshold_high:   Mapped[int]          = mapped_column(SmallInteger, default=65)
    max_score:        Mapped[int]          = mapped_column(SmallInteger, default=100)
    created_by:       Mapped[uuid.UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at:       Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at:       Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    rules:   Mapped[list["AlgorithmRule"]] = relationship(
        back_populates="algorithm", cascade="all, delete",
        order_by="AlgorithmRule.sort_order"
    )
    creator: Mapped["User | None"] = relationship(back_populates="algorithms")


class AlgorithmRule(Base):
    __tablename__ = "algorithm_rules"

    id:           Mapped[uuid.UUID]      = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    algorithm_id: Mapped[uuid.UUID]      = mapped_column(PGUUID(as_uuid=True), ForeignKey("prediction_algorithms.id", ondelete="CASCADE"))
    field:        Mapped[RuleField]      = mapped_column(SAEnum(RuleField), nullable=False)
    operator:     Mapped[RuleOperator]   = mapped_column(SAEnum(RuleOperator), nullable=False)
    value:        Mapped[float | None]   = mapped_column(Numeric(10, 2))
    value_text:   Mapped[str | None]     = mapped_column(Text)
    value2:       Mapped[float | None]   = mapped_column(Numeric(10, 2))
    score:        Mapped[int]            = mapped_column(SmallInteger, nullable=False)
    description:  Mapped[str | None]     = mapped_column(String(300))
    sort_order:   Mapped[int]            = mapped_column(SmallInteger, default=0)
    created_at:   Mapped[datetime]       = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    algorithm: Mapped["PredictionAlgorithm"] = relationship(back_populates="rules")


class Analysis(Base):
    __tablename__ = "analyses"

    id:             Mapped[uuid.UUID]    = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id:     Mapped[uuid.UUID]    = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id:      Mapped[uuid.UUID]    = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    analysis_date:  Mapped[date]         = mapped_column(Date, default=date.today)
    anamnesis:      Mapped[str | None]   = mapped_column(Text)
    glucose:        Mapped[float | None] = mapped_column(Numeric(5, 2))
    cholesterol:    Mapped[float | None] = mapped_column(Numeric(5, 2))
    systolic_bp:    Mapped[int | None]   = mapped_column(SmallInteger)
    diastolic_bp:   Mapped[int | None]   = mapped_column(SmallInteger)
    heart_rate:     Mapped[int | None]   = mapped_column(SmallInteger)
    temperature:    Mapped[float | None] = mapped_column(Numeric(4, 1))
    bmi:            Mapped[float | None] = mapped_column(Numeric(4, 1))
    predictions:    Mapped[list]         = mapped_column(JSON, default=list)
    recommendation: Mapped[str | None]   = mapped_column(Text)
    created_at:     Mapped[datetime]     = mapped_column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="analyses")
    doctor:  Mapped["User"]    = relationship()
