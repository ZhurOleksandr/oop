#!/usr/bin/env python3
"""
init_db.py — Ініціалізація БД MediPredictor
============================================
Не потребує psql або passlib — тільки bcrypt і asyncpg.
Налаштування читаються з backend/.env автоматично.

Використання:
    python init_db.py           — ініціалізувати (якщо вже є — пропускає)
    python init_db.py --reset   — скинути і заповнити заново
"""
import asyncio
import argparse
import uuid
import json
import re
from pathlib import Path
from datetime import date

# ── bcrypt напряму (без passlib) — сумісно з Python 3.13 ────────────────────
import bcrypt

def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(12)).decode("utf-8")

import asyncpg
from config import get_settings

settings = get_settings()
SCHEMA_FILE = Path(__file__).parent.parent / "database" / "schema.sql"


# ── Застосування schema.sql через asyncpg (без psql) ────────────────────────

async def apply_schema(conn: asyncpg.Connection):
    """Читає schema.sql і виконує кожну команду через asyncpg."""
    if not SCHEMA_FILE.exists():
        print(f"   ⚠️  schema.sql не знайдено: {SCHEMA_FILE}")
        return

    print(f"   📄 Застосовуємо: {SCHEMA_FILE.name}")
    sql = SCHEMA_FILE.read_text(encoding="utf-8")

    # Видаляємо коментарі
    sql = re.sub(r'--[^\n]*', '', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

    # Розбиваємо на команди, враховуючи $$ блоки
    statements = []
    current = []
    in_dollar = False

    for line in sql.splitlines():
        count = line.count('$$')
        if count % 2 != 0:
            in_dollar = not in_dollar
        current.append(line)
        if not in_dollar and line.rstrip().endswith(';'):
            stmt = '\n'.join(current).strip()
            if stmt and stmt != ';':
                statements.append(stmt)
            current = []

    ok = 0
    for stmt in statements:
        if not stmt.strip():
            continue
        try:
            await conn.execute(stmt)
            ok += 1
        except Exception as e:
            msg = str(e).lower()
            if any(x in msg for x in ("already exists", "duplicate", "does not exist")):
                ok += 1  # ОК — таблиця/тип вже є
            else:
                print(f"   ⚠️  {e}")

    print(f"   ✅ Схему застосовано ({ok} операцій)")


# ── Головна функція ──────────────────────────────────────────────────────────

async def main(reset: bool = False):
    dsn = settings.db_url.replace("postgresql+asyncpg://", "postgresql://")

    print(f"\n🔌 Підключення: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"   Користувач:  {settings.DB_USER}")

    try:
        conn = await asyncpg.connect(dsn)
    except Exception as e:
        print(f"\n❌ Помилка підключення: {e}")
        print("\n💡 Перевірте backend/.env:")
        print(f"   DB_HOST     = {settings.DB_HOST}")
        print(f"   DB_PORT     = {settings.DB_PORT}")
        print(f"   DB_USER     = {settings.DB_USER}")
        print(f"   DB_PASSWORD = {'*' * len(str(settings.DB_PASSWORD))}")
        print(f"   DB_NAME     = {settings.DB_NAME}")
        print("\n💡 Переконайтесь що PostgreSQL сервіс запущено.")
        raise SystemExit(1)

    print("✅ Підключено\n")

    try:
        if reset:
            print("⚠️  Скидаємо дані...")
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                "WHERE table_name='users' AND table_schema='public')"
            )
            if exists:
                await conn.execute("""
                    TRUNCATE analyses, patients, algorithm_rules,
                             prediction_algorithms, users
                    RESTART IDENTITY CASCADE
                """)
                print("   Таблиці очищено\n")

        # Перевіряємо схему
        print("📋 Перевірка схеми...")
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        )
        existing = {r['tablename'] for r in tables}
        required = {'users','patients','prediction_algorithms','algorithm_rules','analyses'}

        if required - existing:
            print(f"   Відсутні таблиці: {required - existing}")
            print("   Застосовуємо schema.sql...\n")
            await apply_schema(conn)
            print()
        else:
            print("   ✅ Всі таблиці існують\n")

        # ── Користувачі ───────────────────────────────────────────────────
        print("👤 Користувачі...")
        users = [
            ("11111111-0000-0000-0000-000000000001","doctor1","password123",
             "Петренко Олександр Миколайович","doctor","Терапевт"),
            ("11111111-0000-0000-0000-000000000002","admin","admin123",
             "Коваль Марія Іванівна","admin","Адміністратор"),
            ("11111111-0000-0000-0000-000000000003","analyst","analyst123",
             "Сидоренко Іван Петрович","analyst","Аналітик"),
            ("11111111-0000-0000-0000-000000000004","doctor2","password123",
             "Мельник Олена Василівна","doctor","Кардіолог"),
        ]
        for uid, login, pw, name, role, spec in users:
            hashed = hash_pw(pw)
            await conn.execute("""
                INSERT INTO users (id,login,password,full_name,role,specialty)
                VALUES ($1,$2,$3,$4,$5::user_role,$6)
                ON CONFLICT (login) DO UPDATE
                  SET password=EXCLUDED.password,
                      full_name=EXCLUDED.full_name,
                      role=EXCLUDED.role,
                      specialty=EXCLUDED.specialty
            """, uuid.UUID(uid), login, hashed, name, role, spec)
            print(f"   ✅ {login:12s}  ({role})")

        # ── Алгоритми ─────────────────────────────────────────────────────
        print("\n🧠 Системні алгоритми...")
        admin_id = uuid.UUID("11111111-0000-0000-0000-000000000002")

        algos = [
            ("aaaaaaaa-0000-0000-0000-000000000001",
             "Алгоритм: Цукровий діабет 2 типу","Цукровий діабет 2 типу",
             "Rule-based ООП-алгоритм.",20,40,65,115,[
                ("glucose","gt",7.0,None,None,50,"Глюкоза > 7.0"),
                ("glucose","between",6.1,7.0,None,25,"Глюкоза 6.1–7.0 (переддіабет)"),
                ("age","gt",45,None,None,15,"Вік > 45"),
                ("cholesterol","gt",5.5,None,None,10,"Холестерин > 5.5"),
                ("anamnesis","contains",None,None,"спраг,сечовипуск,втом",20,"Симптоми діабету"),
             ]),
            ("aaaaaaaa-0000-0000-0000-000000000002",
             "Алгоритм: Артеріальна гіпертензія","Артеріальна гіпертензія",
             "Оцінка за АТ.",15,35,60,105,[
                ("systolicBP","gt",140,None,None,50,"Систолічний АТ > 140"),
                ("systolicBP","between",130,140,None,25,"Систолічний АТ 130–140"),
                ("diastolicBP","gt",90,None,None,30,"Діастолічний АТ > 90"),
                ("diastolicBP","between",85,90,None,15,"Діастолічний АТ 85–90"),
                ("age","gt",50,None,None,10,"Вік > 50"),
                ("anamnesis","contains",None,None,"тиск,головний,запаморочен,набряк",15,"Симптоми"),
             ]),
            ("aaaaaaaa-0000-0000-0000-000000000003",
             "Алгоритм: Серцево-судинна недостатність","Серцево-судинна недостатність",
             "Оцінка ССН.",20,40,60,110,[
                ("cholesterol","gt",6.5,None,None,40,"Холестерин > 6.5"),
                ("cholesterol","between",5.5,6.5,None,20,"Холестерин 5.5–6.5"),
                ("systolicBP","gt",150,None,None,25,"АТ > 150"),
                ("age","gt",55,None,None,15,"Вік > 55"),
                ("heartRate","gt",100,None,None,15,"ЧСС > 100"),
                ("anamnesis","contains",None,None,"задишк,набряк,серц,кардіо",20,"Симптоми ССН"),
             ]),
            ("aaaaaaaa-0000-0000-0000-000000000004",
             "Алгоритм: Атеросклероз","Атеросклероз",
             "Оцінка за ліпідами.",20,35,55,95,[
                ("cholesterol","gt",6.0,None,None,45,"Холестерин > 6.0"),
                ("cholesterol","between",5.0,6.0,None,20,"Холестерин 5.0–6.0"),
                ("age","gt",50,None,None,20,"Вік > 50"),
                ("systolicBP","gt",140,None,None,15,"АТ > 140"),
                ("glucose","gt",6.0,None,None,10,"Глюкоза > 6.0"),
             ]),
            ("aaaaaaaa-0000-0000-0000-000000000005",
             "Алгоритм: Метаболічний синдром","Метаболічний синдром",
             "Метаболічні порушення.",20,45,70,120,[
                ("glucose","gt",6.1,None,None,30,"Глюкоза > 6.1"),
                ("cholesterol","gt",5.5,None,None,25,"Холестерин > 5.5"),
                ("systolicBP","gt",130,None,None,25,"АТ > 130"),
                ("bmi","gt",30,None,None,25,"ІМТ > 30"),
                ("age","gt",40,None,None,10,"Вік > 40"),
             ]),
        ]

        for (aid_s, name, disease, desc, tl, tm, th, mx, rules) in algos:
            aid = uuid.UUID(aid_s)
            await conn.execute("""
                INSERT INTO prediction_algorithms
                  (id,name,disease,description,version,is_system,
                   threshold_low,threshold_medium,threshold_high,max_score,created_by)
                VALUES ($1,$2,$3,$4,'1.0',TRUE,$5,$6,$7,$8,$9)
                ON CONFLICT (id) DO UPDATE
                  SET name=EXCLUDED.name, disease=EXCLUDED.disease,
                      threshold_low=EXCLUDED.threshold_low,
                      threshold_medium=EXCLUDED.threshold_medium,
                      threshold_high=EXCLUDED.threshold_high,
                      max_score=EXCLUDED.max_score
            """, aid, name, disease, desc, tl, tm, th, mx, admin_id)

            await conn.execute(
                "DELETE FROM algorithm_rules WHERE algorithm_id=$1", aid
            )
            for i, (field,op,val,val2,vt,score,rdesc) in enumerate(rules):
                await conn.execute("""
                    INSERT INTO algorithm_rules
                      (algorithm_id,field,operator,value,value2,
                       value_text,score,description,sort_order)
                    VALUES ($1,$2::rule_field,$3::rule_operator,$4,$5,$6,$7,$8,$9)
                """, aid, field, op,
                    float(val) if val is not None else None,
                    float(val2) if val2 is not None else None,
                    vt, score, rdesc, i)

            print(f"   ✅ {disease}")

        # ── Тестові пацієнти ──────────────────────────────────────────────
        print("\n👥 Тестові пацієнти...")
        doc1 = uuid.UUID("11111111-0000-0000-0000-000000000001")
        for pid_s, nm, age, gender, phone in [
            ("bbbbbbbb-0000-0000-0000-000000000001","Іванов Іван Іванович",52,"male","+380501234567"),
            ("bbbbbbbb-0000-0000-0000-000000000002","Петренко Олена Сергіївна",45,"female","+380671234568"),
            ("bbbbbbbb-0000-0000-0000-000000000003","Кравченко Микола Петрович",61,"male","+380931234569"),
        ]:
            await conn.execute("""
                INSERT INTO patients (id,full_name,age,gender,phone,doctor_id)
                VALUES ($1,$2,$3,$4::gender_type,$5,$6)
                ON CONFLICT (id) DO UPDATE SET full_name=EXCLUDED.full_name
            """, uuid.UUID(pid_s), nm, age, gender, phone, doc1)
            print(f"   ✅ {nm}")

        # ── Тестові аналізи ───────────────────────────────────────────────
        print("\n🔬 Тестові аналізи...")
        p1 = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")
        p2 = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")

        for pid, adate, anamnesis, glucose, chol, sys_bp, dia_bp, hr, preds_list, reco in [
            (p1, date(2024,5,10),
             "Скарги на задишку, набряки ніг, підвищений тиск",
             5.8, 6.2, 160, 100, 88,
             [{"disease":"Артеріальна гіпертензія","probability":85,"risk":"high",
               "score":85,"max_score":105,"factors":["АТ сист. > 140","АТ діаст. > 90"]},
              {"disease":"Серцево-судинна недостатність","probability":60,"risk":"medium",
               "score":65,"max_score":110,"factors":["Холестерин 5.5–6.5","Вік > 55"]}],
             "Консультація кардіолога. Добовий моніторинг АТ. Повторний огляд через 3 місяці."),
            (p2, date(2024,5,12),
             "Підвищена спрага, часте сечовипускання, втома",
             8.9, 5.1, 130, 85, 78,
             [{"disease":"Цукровий діабет 2 типу","probability":92,"risk":"high",
               "score":105,"max_score":115,"factors":["Глюкоза > 7.0","Вік > 45","Симптоми діабету"]},
              {"disease":"Метаболічний синдром","probability":55,"risk":"medium",
               "score":66,"max_score":120,"factors":["Глюкоза > 6.1","АТ > 130"]}],
             "Направити до ендокринолога. Контроль глікемії. Повторний огляд через 1 місяць."),
        ]:
            await conn.execute("""
                INSERT INTO analyses
                  (patient_id,doctor_id,analysis_date,anamnesis,
                   glucose,cholesterol,systolic_bp,diastolic_bp,
                   heart_rate,predictions,recommendation)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10::jsonb,$11)
                ON CONFLICT DO NOTHING
            """, pid, doc1, adate, anamnesis,
                glucose, chol, sys_bp, dia_bp, hr,
                json.dumps(preds_list), reco)
            print(f"   ✅ Аналіз від {adate}")

        print()
        print("=" * 46)
        print("✅ База даних ініціалізована успішно!")
        print("=" * 46)
        print()
        print("📋 Акаунти для входу:")
        print("   doctor1  / password123  🩺  Лікар")
        print("   admin    / admin123     ⚙️   Адмін")
        print("   analyst  / analyst123   📊  Аналітик")

    finally:
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Скинути всі дані")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
