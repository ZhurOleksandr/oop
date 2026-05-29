"""
pytest configuration and shared fixtures.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import AsyncMock, MagicMock
from database import User, UserRole


@pytest.fixture
def doctor_user():
    user = MagicMock(spec=User)
    user.id = "11111111-0000-0000-0000-000000000001"
    user.login = "doctor1"
    user.full_name = "Петренко Олександр Миколайович"
    user.role = UserRole.doctor
    user.specialty = "Терапевт"
    user.is_active = True
    return user


@pytest.fixture
def admin_user():
    user = MagicMock(spec=User)
    user.id = "11111111-0000-0000-0000-000000000002"
    user.login = "admin"
    user.full_name = "Коваль Марія Іванівна"
    user.role = UserRole.admin
    user.specialty = "Адміністратор"
    user.is_active = True
    return user


@pytest.fixture
def analyst_user():
    user = MagicMock(spec=User)
    user.id = "11111111-0000-0000-0000-000000000003"
    user.login = "analyst"
    user.full_name = "Сидоренко Іван Петрович"
    user.role = UserRole.analyst
    user.specialty = "Аналітик"
    user.is_active = True
    return user


@pytest.fixture
def sample_patient_data():
    """Standard patient data for prediction tests."""
    from predictor import PatientData
    return PatientData(
        glucose=8.9,
        cholesterol=5.1,
        systolicBP=130,
        diastolicBP=85,
        heart_rate=78,
        temperature=36.6,
        bmi=27.5,
        age=45,
        gender="female",
        anamnesis="Підвищена спрага, часте сечовипускання, втома"
    )
