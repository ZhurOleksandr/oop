"""
Unit tests for Pydantic schemas validation.
Run: pytest backend/tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from pydantic import ValidationError
from schemas import (
    PatientCreate, AlgorithmCreate, RuleCreate, AnalysisCreate,
    UserCreate, LoginRequest
)
from database import GenderType, RuleField, RuleOperator, UserRole
import uuid


# ── PatientCreate ──────────────────────────────────────────────────────────

class TestPatientCreate:

    def test_valid_patient(self):
        p = PatientCreate(full_name="Іван Іванов", age=45, gender=GenderType.male)
        assert p.full_name == "Іван Іванов"
        assert p.age == 45

    def test_age_too_low(self):
        with pytest.raises(ValidationError):
            PatientCreate(full_name="Test", age=-1, gender=GenderType.male)

    def test_age_too_high(self):
        with pytest.raises(ValidationError):
            PatientCreate(full_name="Test", age=200, gender=GenderType.male)

    def test_name_too_short(self):
        with pytest.raises(ValidationError):
            PatientCreate(full_name="A", age=30, gender=GenderType.female)

    def test_optional_phone(self):
        p = PatientCreate(full_name="Test Patient", age=30, gender=GenderType.female, phone="+380501234567")
        assert p.phone == "+380501234567"

    def test_phone_optional(self):
        p = PatientCreate(full_name="Test Patient", age=30, gender=GenderType.female)
        assert p.phone is None


# ── RuleCreate ─────────────────────────────────────────────────────────────

class TestRuleCreate:

    def test_valid_numeric_rule(self):
        r = RuleCreate(
            field=RuleField.glucose,
            operator=RuleOperator.gt,
            value=7.0,
            score=50
        )
        assert r.score == 50
        assert r.value == 7.0

    def test_valid_text_rule(self):
        r = RuleCreate(
            field=RuleField.anamnesis,
            operator=RuleOperator.contains,
            value_text="спраг,втом",
            score=20
        )
        assert r.value_text == "спраг,втом"

    def test_score_too_low(self):
        with pytest.raises(ValidationError):
            RuleCreate(field=RuleField.glucose, operator=RuleOperator.gt, score=0)

    def test_score_too_high(self):
        with pytest.raises(ValidationError):
            RuleCreate(field=RuleField.glucose, operator=RuleOperator.gt, score=999)

    def test_between_rule(self):
        r = RuleCreate(
            field=RuleField.systolicBP,
            operator=RuleOperator.between,
            value=130,
            value2=140,
            score=25
        )
        assert r.value == 130
        assert r.value2 == 140


# ── AlgorithmCreate ────────────────────────────────────────────────────────

class TestAlgorithmCreate:

    def _base_algo(self, **kwargs):
        defaults = dict(
            name="Test Algorithm",
            disease="Test Disease",
            threshold_low=20,
            threshold_medium=40,
            threshold_high=65,
            max_score=100,
            rules=[]
        )
        defaults.update(kwargs)
        return AlgorithmCreate(**defaults)

    def test_valid_algorithm(self):
        algo = self._base_algo()
        assert algo.name == "Test Algorithm"
        assert algo.disease == "Test Disease"

    def test_high_threshold_must_exceed_medium(self):
        with pytest.raises(ValidationError):
            self._base_algo(threshold_medium=60, threshold_high=50)

    def test_name_too_short(self):
        with pytest.raises(ValidationError):
            self._base_algo(name="AB")

    def test_with_rules(self):
        rules = [
            RuleCreate(field=RuleField.glucose, operator=RuleOperator.gt, value=7.0, score=50),
            RuleCreate(field=RuleField.age, operator=RuleOperator.gt, value=45, score=15),
        ]
        algo = self._base_algo(rules=rules)
        assert len(algo.rules) == 2

    def test_max_score_positive(self):
        with pytest.raises(ValidationError):
            self._base_algo(max_score=0)

    def test_version_default(self):
        algo = self._base_algo()
        assert algo.version == "1.0"


# ── AnalysisCreate ─────────────────────────────────────────────────────────

class TestAnalysisCreate:

    def _patient_id(self):
        return uuid.uuid4()

    def test_valid_minimal(self):
        a = AnalysisCreate(patient_id=self._patient_id())
        assert a.glucose is None

    def test_glucose_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisCreate(patient_id=self._patient_id(), glucose=100.0)

    def test_bp_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisCreate(patient_id=self._patient_id(), systolic_bp=400)

    def test_all_indicators(self):
        a = AnalysisCreate(
            patient_id=self._patient_id(),
            glucose=6.5,
            cholesterol=5.2,
            systolic_bp=130,
            diastolic_bp=85,
            heart_rate=72,
            temperature=36.6,
            bmi=24.5
        )
        assert a.glucose == 6.5
        assert a.bmi == 24.5

    def test_temperature_out_of_range(self):
        with pytest.raises(ValidationError):
            AnalysisCreate(patient_id=self._patient_id(), temperature=50.0)

    def test_negative_bmi(self):
        with pytest.raises(ValidationError):
            AnalysisCreate(patient_id=self._patient_id(), bmi=-1.0)


# ── UserCreate ─────────────────────────────────────────────────────────────

class TestUserCreate:

    def test_valid_doctor(self):
        u = UserCreate(
            login="newdoc",
            password="securepass",
            full_name="Новий Лікар",
            role=UserRole.doctor
        )
        assert u.login == "newdoc"
        assert u.role == UserRole.doctor

    def test_login_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(login="ab", password="securepass", full_name="Test User")

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(login="validlogin", password="123", full_name="Test User")

    def test_default_role_is_doctor(self):
        u = UserCreate(login="testlogin", password="password123", full_name="Test User")
        assert u.role == UserRole.doctor


# ── LoginRequest ───────────────────────────────────────────────────────────

class TestLoginRequest:

    def test_valid_login(self):
        lr = LoginRequest(login="doctor1", password="password123")
        assert lr.login == "doctor1"

    def test_fields_present(self):
        lr = LoginRequest(login="admin", password="admin123")
        assert hasattr(lr, "login")
        assert hasattr(lr, "password")
