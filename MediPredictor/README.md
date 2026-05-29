# 🏥 MediPredictor
**Інформаційна система прогнозування та аналізу захворювань**  
*із використанням технології об'єктно-орієнтованого програмування*

> Студент: Журавель Олександр Сергійович, група аІк-43

---

## 🏗️ ООП-архітектура (predictor.py)

```
BasePredictor  (ABC — абстрактний базовий клас)
├── predict(patient) → PredictionResult | None   [абстрактний]
├── get_disease_name() → str                      [абстрактний]
└── is_active: bool                               [абстрактний]
     │
     └── RuleBasedPredictor  (конкретна реалізація — наслідування)
         ├── __init__(algorithm: PredictionAlgorithm)
         ├── predict()          ← головна логіка обчислення балів
         ├── _compute_risk()    ← захищений метод (інкапсуляція)
         └── _normalize_probability()  ← захищений метод

PatientData      (dataclass — інкапсуляція вхідних даних)
├── get_field(name) → Any     ← уніфікований доступ до показників
├── has_indicator(name) → bool
└── summary() → str

PredictionResult (dataclass — інкапсуляція результату)
├── to_dict() → dict          ← серіалізація для PostgreSQL JSONB
└── is_significant: bool      ← property

RuleEvaluator    (клас-стратегія — Strategy pattern)
└── evaluate(rule, patient) → (bool, str)

RecommendationBuilder  (Builder pattern)
├── add_for_diseases(diseases) → self
├── add_followup(months) → self
└── build() → str

PredictionEngine  (Facade pattern — координатор)
├── __init__(algorithms)   ← поліморфізм: зберігає BasePredictor[]
├── run(patient) → (list[dict], str)
└── predictor_count: int
```

### Принципи ООП у проєкті:

| Принцип | Де реалізовано |
|---------|---------------|
| **Абстракція** | `BasePredictor` — ABC з абстрактними методами `predict()`, `get_disease_name()`, `is_active` |
| **Інкапсуляція** | `PatientData.get_field()` ховає маппінг; `RuleBasedPredictor._compute_risk()` — захищені методи |
| **Наслідування** | `RuleBasedPredictor(BasePredictor)` — конкретна реалізація |
| **Поліморфізм** | `PredictionEngine` викликає `predictor.predict()` для будь-якого `BasePredictor` |

---

## 📁 Структура проєкту

```
MediPredictor/
├── start.py              ← ЄДИНА ТОЧКА ЗАПУСКУ
│
├── database/
│   ├── schema.sql        ← DDL: таблиці, індекси, тригери, VIEW
│   └── seed.sql          ← Дані: алгоритми, тестові акаунти
│
├── backend/
│   ├── main.py           ← FastAPI app + middleware
│   ├── config.py         ← Pydantic Settings
│   ├── database.py       ← SQLAlchemy ORM моделі
│   ├── auth.py           ← JWT, bcrypt, role-guards
│   ├── schemas.py        ← Pydantic v2 схеми
│   ├── predictor.py      ← ООП prediction engine (ABC, наслідування, поліморфізм)
│   ├── middleware.py     ← Timing, security headers, audit log
│   ├── init_db.py        ← Ініціалізація БД з bcrypt хешами
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── patients.py
│   │   ├── algorithms.py
│   │   └── analyses.py / stats.py
│   └── tests/
│       ├── test_predictor.py  ← ООП тести (50+ тестів)
│       ├── test_schemas.py
│       ├── test_auth.py
│       ├── test_api.py
│       └── conftest.py
│
└── frontend/
    └── index.html        ← SPA: дашборд, аналіз, алгоритми, адмін
```

---

## ⚡ Запуск (без Docker — один файл!)

```bash
# Крок 1: PostgreSQL
psql -U postgres -c "CREATE USER mediuser WITH PASSWORD 'medipassword';"
psql -U postgres -c "CREATE DATABASE medipredictor OWNER mediuser;"
psql -U mediuser -d medipredictor -f database/schema.sql

# Крок 2: Запустити всю систему одною командою
python start.py
```

`start.py` автоматично:
- Перевіряє Python 3.10+
- Створює venv та встановлює залежності
- Генерує SECRET_KEY у `.env`
- Запускає `init_db.py` (bcrypt паролі + seed дані)
- Стартує uvicorn сервер

Після запуску:
- **API:**    http://localhost:8000
- **Swagger** http://localhost:8000/docs
- **Frontend:** відкрити `frontend/index.html` у браузері

---

## 🔐 Акаунти

| Роль | Логін | Пароль |
|------|-------|--------|
| 🩺 Лікар | `doctor1` | `password123` |
| ⚙️ Адмін | `admin` | `admin123` |
| 📊 Аналітик | `analyst` | `analyst123` |

---

## 🧠 Алгоритми прогнозування

5 системних алгоритмів + необмежено кастомних (лікарі/адміни):

| Захворювання | Показники |
|-------------|-----------|
| Цукровий діабет 2 типу | Глюкоза, вік, анамнез |
| Артеріальна гіпертензія | АТ сист./діаст., вік, анамнез |
| Серцево-судинна недостатність | Холестерин, АТ, ЧСС, вік |
| Атеросклероз | Холестерин, вік, АТ, глюкоза |
| Метаболічний синдром | Глюкоза, холестерин, АТ, ІМТ |

---

## 🧪 Тести

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

~120 тестів: predictor engine, Pydantic schemas, JWT/bcrypt, API endpoints.

---

## 🔌 API

```
POST /api/auth/login              → JWT token
GET  /api/patients/               → список пацієнтів
POST /api/patients/               → створити пацієнта
POST /api/analyses/               → аналіз + ООП prediction engine
GET  /api/algorithms/             → всі алгоритми
POST /api/algorithms/             → створити алгоритм (лікар/адмін)
PUT  /api/algorithms/{id}         → оновити
POST /api/algorithms/{id}/toggle  → вмикнути/вимкнути
GET  /api/stats/                  → статистика
```

Swagger UI: http://localhost:8000/docs
