-- ============================================================
-- MediPredictor v2.0 — Quick Seed (for development only)
-- ⚠️  IMPORTANT: Passwords here are SHA-256 placeholders.
--    For production use, run: python backend/init_db.py
--    That script generates proper bcrypt hashes at runtime.
-- ============================================================

-- These bcrypt hashes correspond to:
--   doctor1  / password123
--   admin    / admin123
--   analyst  / analyst123
--   doctor2  / password123
-- Generated with bcrypt cost=12. Replace if needed via init_db.py

INSERT INTO users (id, login, password, full_name, role, specialty) VALUES
(
  '11111111-0000-0000-0000-000000000001',
  'doctor1',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdHnl87DadDOIyK',
  'Петренко Олександр Миколайович', 'doctor', 'Терапевт'
),
(
  '11111111-0000-0000-0000-000000000002',
  'admin',
  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
  'Коваль Марія Іванівна', 'admin', 'Головний адміністратор'
),
(
  '11111111-0000-0000-0000-000000000003',
  'analyst',
  '$2b$12$KrixAaJBQCGZRYHl9cqar.A2WQFN1CWvVReyy/8YSQWi6N89zP5.',
  'Сидоренко Іван Петрович', 'analyst', 'Медичний аналітик'
),
(
  '11111111-0000-0000-0000-000000000004',
  'doctor2',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdHnl87DadDOIyK',
  'Мельник Олена Василівна', 'doctor', 'Кардіолог'
)
ON CONFLICT (login) DO NOTHING;

-- ── Algorithm: Цукровий діабет 2 типу ────────────────────────
INSERT INTO prediction_algorithms
  (id, name, disease, description, version, is_system,
   threshold_low, threshold_medium, threshold_high, max_score, created_by)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000001',
  'Алгоритм: Цукровий діабет 2 типу',
  'Цукровий діабет 2 типу',
  'Rule-based алгоритм визначення ризику ЦД-2 на основі глюкози крові, віку, холестерину та клінічних симптомів.',
  '1.0', TRUE, 20, 40, 65, 115,
  '11111111-0000-0000-0000-000000000002'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO algorithm_rules
  (algorithm_id, field, operator, value, value2, value_text, score, description, sort_order)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001','glucose',    'gt',      7.0,  NULL, NULL,                  50, 'Глюкоза > 7.0 ммоль/л (діабетична норма)',    1),
  ('aaaaaaaa-0000-0000-0000-000000000001','glucose',    'between', 6.1,  7.0,  NULL,                  25, 'Глюкоза 6.1–7.0 ммоль/л (переддіабет)',       2),
  ('aaaaaaaa-0000-0000-0000-000000000001','age',        'gt',      45,   NULL, NULL,                  15, 'Вік > 45 років',                              3),
  ('aaaaaaaa-0000-0000-0000-000000000001','cholesterol','gt',      5.5,  NULL, NULL,                  10, 'Холестерин > 5.5 ммоль/л',                    4),
  ('aaaaaaaa-0000-0000-0000-000000000001','anamnesis',  'contains',NULL, NULL, 'спраг,сечовипуск,втом', 20,'Симптоми: спрага, сечовипускання, втома',     5);

-- ── Algorithm: Артеріальна гіпертензія ───────────────────────
INSERT INTO prediction_algorithms
  (id, name, disease, description, version, is_system,
   threshold_low, threshold_medium, threshold_high, max_score, created_by)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000002',
  'Алгоритм: Артеріальна гіпертензія',
  'Артеріальна гіпертензія',
  'Визначення ризику гіпертензії на основі АТ, віку та симптомів.',
  '1.0', TRUE, 15, 35, 60, 105,
  '11111111-0000-0000-0000-000000000002'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO algorithm_rules
  (algorithm_id, field, operator, value, value2, value_text, score, description, sort_order)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000002','systolicBP', 'gt',      140, NULL, NULL,                          50, 'Систолічний АТ > 140 мм рт.ст.',        1),
  ('aaaaaaaa-0000-0000-0000-000000000002','systolicBP', 'between', 130, 140,  NULL,                          25, 'Систолічний АТ 130–140 (передгіпертензія)',2),
  ('aaaaaaaa-0000-0000-0000-000000000002','diastolicBP','gt',      90,  NULL, NULL,                          30, 'Діастолічний АТ > 90 мм рт.ст.',        3),
  ('aaaaaaaa-0000-0000-0000-000000000002','diastolicBP','between', 85,  90,   NULL,                          15, 'Діастолічний АТ 85–90',                  4),
  ('aaaaaaaa-0000-0000-0000-000000000002','age',        'gt',      50,  NULL, NULL,                          10, 'Вік > 50 років',                         5),
  ('aaaaaaaa-0000-0000-0000-000000000002','anamnesis',  'contains',NULL,NULL, 'тиск,головний,запаморочен,набряк',15,'Симптоми гіпертензії',                6);

-- ── Algorithm: Серцево-судинна недостатність ─────────────────
INSERT INTO prediction_algorithms
  (id, name, disease, description, version, is_system,
   threshold_low, threshold_medium, threshold_high, max_score, created_by)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000003',
  'Алгоритм: Серцево-судинна недостатність',
  'Серцево-судинна недостатність',
  'Комплексний алгоритм оцінки ризику ССН за холестерином, АТ, ЧСС та анамнезом.',
  '1.0', TRUE, 20, 40, 60, 110,
  '11111111-0000-0000-0000-000000000002'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO algorithm_rules
  (algorithm_id, field, operator, value, value2, value_text, score, description, sort_order)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000003','cholesterol','gt',      6.5, NULL, NULL,                           40,'Холестерин > 6.5 ммоль/л',              1),
  ('aaaaaaaa-0000-0000-0000-000000000003','cholesterol','between', 5.5, 6.5,  NULL,                           20,'Холестерин 5.5–6.5 ммоль/л',            2),
  ('aaaaaaaa-0000-0000-0000-000000000003','systolicBP', 'gt',      150, NULL, NULL,                           25,'Систолічний АТ > 150 мм рт.ст.',        3),
  ('aaaaaaaa-0000-0000-0000-000000000003','age',        'gt',      55,  NULL, NULL,                           15,'Вік > 55 років',                         4),
  ('aaaaaaaa-0000-0000-0000-000000000003','heartRate',  'gt',      100, NULL, NULL,                           15,'ЧСС > 100 уд/хв (тахікардія)',           5),
  ('aaaaaaaa-0000-0000-0000-000000000003','anamnesis',  'contains',NULL,NULL, 'задишк,набряк,серц,кардіо',    20,'Симптоми: задишка, набряки, серцебиття', 6);

-- ── Algorithm: Атеросклероз ───────────────────────────────────
INSERT INTO prediction_algorithms
  (id, name, disease, description, version, is_system,
   threshold_low, threshold_medium, threshold_high, max_score, created_by)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000004',
  'Алгоритм: Атеросклероз',
  'Атеросклероз',
  'Оцінка ризику атеросклерозу за рівнем ліпідів, віком та АТ.',
  '1.0', TRUE, 20, 35, 55, 95,
  '11111111-0000-0000-0000-000000000002'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO algorithm_rules
  (algorithm_id, field, operator, value, value2, value_text, score, description, sort_order)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000004','cholesterol','gt',      6.0, NULL, NULL, 45,'Холестерин > 6.0 ммоль/л',        1),
  ('aaaaaaaa-0000-0000-0000-000000000004','cholesterol','between', 5.0, 6.0,  NULL, 20,'Холестерин 5.0–6.0 ммоль/л',      2),
  ('aaaaaaaa-0000-0000-0000-000000000004','age',        'gt',      50,  NULL, NULL, 20,'Вік > 50 років',                  3),
  ('aaaaaaaa-0000-0000-0000-000000000004','systolicBP', 'gt',      140, NULL, NULL, 15,'Систолічний АТ > 140 мм рт.ст.', 4),
  ('aaaaaaaa-0000-0000-0000-000000000004','glucose',    'gt',      6.0, NULL, NULL, 10,'Глюкоза > 6.0 (асоційований ризик)',5);

-- ── Algorithm: Метаболічний синдром ──────────────────────────
INSERT INTO prediction_algorithms
  (id, name, disease, description, version, is_system,
   threshold_low, threshold_medium, threshold_high, max_score, created_by)
VALUES (
  'aaaaaaaa-0000-0000-0000-000000000005',
  'Алгоритм: Метаболічний синдром',
  'Метаболічний синдром',
  'Комплексна оцінка метаболічних порушень: глюкоза, АТ, холестерин, ІМТ.',
  '1.0', TRUE, 20, 45, 70, 120,
  '11111111-0000-0000-0000-000000000002'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO algorithm_rules
  (algorithm_id, field, operator, value, value2, value_text, score, description, sort_order)
VALUES
  ('aaaaaaaa-0000-0000-0000-000000000005','glucose',    'gt', 6.1,  NULL, NULL, 30,'Глюкоза > 6.1 ммоль/л',           1),
  ('aaaaaaaa-0000-0000-0000-000000000005','cholesterol','gt', 5.5,  NULL, NULL, 25,'Холестерин > 5.5 ммоль/л',         2),
  ('aaaaaaaa-0000-0000-0000-000000000005','systolicBP', 'gt', 130,  NULL, NULL, 25,'АТ систолічний > 130 мм рт.ст.',   3),
  ('aaaaaaaa-0000-0000-0000-000000000005','bmi',        'gt', 30,   NULL, NULL, 25,'ІМТ > 30 (ожиріння)',              4),
  ('aaaaaaaa-0000-0000-0000-000000000005','age',        'gt', 40,   NULL, NULL, 10,'Вік > 40 років',                   5);

-- ── Sample Patients ───────────────────────────────────────────
INSERT INTO patients (id, full_name, age, gender, phone, doctor_id) VALUES
  ('bbbbbbbb-0000-0000-0000-000000000001','Іванов Іван Іванович',        52,'male',  '+380501234567','11111111-0000-0000-0000-000000000001'),
  ('bbbbbbbb-0000-0000-0000-000000000002','Петренко Олена Сергіївна',    45,'female','+380671234568','11111111-0000-0000-0000-000000000001'),
  ('bbbbbbbb-0000-0000-0000-000000000003','Кравченко Микола Петрович',   61,'male',  '+380931234569','11111111-0000-0000-0000-000000000001'),
  ('bbbbbbbb-0000-0000-0000-000000000004','Шевченко Тетяна Олексіївна', 38,'female','+380631234570','11111111-0000-0000-0000-000000000004')
ON CONFLICT (id) DO NOTHING;

-- ── Sample Analyses ───────────────────────────────────────────
INSERT INTO analyses
  (patient_id, doctor_id, analysis_date, anamnesis,
   glucose, cholesterol, systolic_bp, diastolic_bp, heart_rate,
   predictions, recommendation)
VALUES
(
  'bbbbbbbb-0000-0000-0000-000000000001',
  '11111111-0000-0000-0000-000000000001',
  '2024-05-10',
  'Скарги на задишку, набряки ніг, підвищений тиск',
  5.8, 6.2, 160, 100, 88,
  '[
    {"disease":"Артеріальна гіпертензія","probability":85,"risk":"high","score":85,"max_score":105,"factors":["Систолічний АТ > 140 мм рт.ст.","Діастолічний АТ > 90 мм рт.ст.","Вік > 50 років"]},
    {"disease":"Серцево-судинна недостатність","probability":60,"risk":"medium","score":65,"max_score":110,"factors":["Холестерин 5.5–6.5 ммоль/л","Вік > 55 років"]},
    {"disease":"Атеросклероз","probability":42,"risk":"medium","score":40,"max_score":95,"factors":["Холестерин 5.0–6.0 ммоль/л","Вік > 50 років"]}
  ]'::jsonb,
  'Консультація кардіолога. Добовий моніторинг АТ. Дієта з обмеженням солі до 5г/добу. Повторний огляд через 3 місяці.'
),
(
  'bbbbbbbb-0000-0000-0000-000000000002',
  '11111111-0000-0000-0000-000000000001',
  '2024-05-12',
  'Підвищена спрага, часте сечовипускання, втома',
  8.9, 5.1, 130, 85, 78,
  '[
    {"disease":"Цукровий діабет 2 типу","probability":92,"risk":"high","score":105,"max_score":115,"factors":["Глюкоза > 7.0 ммоль/л","Вік > 45 років","Симптоми: спрага, сечовипускання, втома"]},
    {"disease":"Метаболічний синдром","probability":55,"risk":"medium","score":66,"max_score":120,"factors":["Глюкоза > 6.1 ммоль/л","АТ систолічний > 130 мм рт.ст."]},
    {"disease":"Артеріальна гіпертензія","probability":24,"risk":"low","score":25,"max_score":105,"factors":["Систолічний АТ 130–140 (передгіпертензія)"]}
  ]'::jsonb,
  'Направити до ендокринолога. Контроль глікемії натще та після їжі. Дієта з обмеженням простих вуглеводів. Повторний огляд через 1 місяць.'
);

SELECT 'Seed data inserted successfully ✅' AS status;
