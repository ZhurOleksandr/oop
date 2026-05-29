-- ============================================================
-- MediPredictor v2.0 — PostgreSQL Schema
-- Run: psql -U mediuser -d medipredictor -f schema.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Enum Types ────────────────────────────────────────────────
DO $$ BEGIN
  CREATE TYPE user_role    AS ENUM ('doctor', 'admin', 'analyst');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE gender_type  AS ENUM ('male', 'female');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE rule_operator AS ENUM (
    'gt', 'gte', 'lt', 'lte', 'eq', 'between', 'contains', 'not_contains'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE rule_field AS ENUM (
    'glucose', 'cholesterol', 'systolicBP', 'diastolicBP',
    'age', 'gender', 'anamnesis', 'bmi', 'heartRate', 'temperature'
  );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── users ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    login       VARCHAR(64)  UNIQUE NOT NULL,
    password    VARCHAR(128) NOT NULL,           -- bcrypt hash
    full_name   VARCHAR(200) NOT NULL,
    role        user_role    NOT NULL DEFAULT 'doctor',
    specialty   VARCHAR(100),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── patients ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name   VARCHAR(200) NOT NULL,
    age         SMALLINT     NOT NULL CHECK (age BETWEEN 0 AND 150),
    gender      gender_type  NOT NULL,
    phone       VARCHAR(20),
    address     TEXT,
    doctor_id   UUID         NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patients_doctor ON patients(doctor_id);

-- ── prediction_algorithms ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS prediction_algorithms (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name             VARCHAR(200) NOT NULL,
    disease          VARCHAR(200) NOT NULL,
    description      TEXT,
    version          VARCHAR(20)  NOT NULL DEFAULT '1.0',
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    is_system        BOOLEAN      NOT NULL DEFAULT FALSE,
    threshold_low    SMALLINT     NOT NULL DEFAULT 20,
    threshold_medium SMALLINT     NOT NULL DEFAULT 40,
    threshold_high   SMALLINT     NOT NULL DEFAULT 65,
    max_score        SMALLINT     NOT NULL DEFAULT 100,
    created_by       UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── algorithm_rules ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS algorithm_rules (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    algorithm_id UUID        NOT NULL REFERENCES prediction_algorithms(id) ON DELETE CASCADE,
    field        rule_field  NOT NULL,
    operator     rule_operator NOT NULL,
    value        NUMERIC(10,2),
    value_text   TEXT,                  -- for 'contains' / 'not_contains'
    value2       NUMERIC(10,2),         -- upper bound for 'between'
    score        SMALLINT    NOT NULL,
    description  VARCHAR(300),
    sort_order   SMALLINT    NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rules_algorithm ON algorithm_rules(algorithm_id);

-- ── analyses ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analyses (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id     UUID        NOT NULL REFERENCES patients(id)  ON DELETE CASCADE,
    doctor_id      UUID        NOT NULL REFERENCES users(id)     ON DELETE RESTRICT,
    analysis_date  DATE        NOT NULL DEFAULT CURRENT_DATE,
    anamnesis      TEXT,
    -- indicators
    glucose        NUMERIC(5,2),   -- mmol/L
    cholesterol    NUMERIC(5,2),   -- mmol/L
    systolic_bp    SMALLINT,       -- mmHg
    diastolic_bp   SMALLINT,       -- mmHg
    heart_rate     SMALLINT,       -- bpm
    temperature    NUMERIC(4,1),   -- Celsius
    bmi            NUMERIC(4,1),   -- kg/m²
    -- results
    predictions    JSONB       NOT NULL DEFAULT '[]',
    recommendation TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_patient ON analyses(patient_id);
CREATE INDEX IF NOT EXISTS idx_analyses_doctor  ON analyses(doctor_id);
CREATE INDEX IF NOT EXISTS idx_analyses_date    ON analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_preds   ON analyses USING GIN(predictions);

-- ── audit_log ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id         BIGSERIAL PRIMARY KEY,
    user_id    UUID REFERENCES users(id),
    action     VARCHAR(100) NOT NULL,
    entity     VARCHAR(100),
    entity_id  UUID,
    details    JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_user   ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_date   ON audit_log(created_at DESC);

-- ── updated_at trigger ───────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

DROP TRIGGER IF EXISTS trg_users_upd    ON users;
DROP TRIGGER IF EXISTS trg_patients_upd ON patients;
DROP TRIGGER IF EXISTS trg_algo_upd     ON prediction_algorithms;

CREATE TRIGGER trg_users_upd
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_patients_upd
  BEFORE UPDATE ON patients
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_algo_upd
  BEFORE UPDATE ON prediction_algorithms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── view: v_patient_summary ───────────────────────────────────
CREATE OR REPLACE VIEW v_patient_summary AS
SELECT
    p.id,
    p.full_name,
    p.age,
    p.gender,
    p.phone,
    p.doctor_id,
    u.full_name                                       AS doctor_name,
    p.created_at,
    COUNT(a.id)                                       AS total_analyses,
    MAX(a.analysis_date)                              AS last_analysis_date,
    (
        SELECT a2.predictions -> 0 ->> 'disease'
        FROM   analyses a2
        WHERE  a2.patient_id = p.id
        ORDER  BY a2.analysis_date DESC, a2.created_at DESC
        LIMIT  1
    )                                                 AS top_disease,
    (
        SELECT a2.predictions -> 0 ->> 'risk'
        FROM   analyses a2
        WHERE  a2.patient_id = p.id
        ORDER  BY a2.analysis_date DESC, a2.created_at DESC
        LIMIT  1
    )                                                 AS top_risk,
    (
        SELECT (a2.predictions -> 0 ->> 'probability')::INT
        FROM   analyses a2
        WHERE  a2.patient_id = p.id
        ORDER  BY a2.analysis_date DESC, a2.created_at DESC
        LIMIT  1
    )                                                 AS top_probability
FROM patients p
JOIN users u ON u.id = p.doctor_id
LEFT JOIN analyses a ON a.patient_id = p.id
GROUP BY p.id, u.full_name;

-- Done!
SELECT 'Schema created successfully ✅' AS status;
