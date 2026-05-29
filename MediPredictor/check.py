#!/usr/bin/env python3
"""
check.py — Діагностика MediPredictor
Запустіть: python check.py
"""
import sys, os, subprocess, socket, re
from pathlib import Path

ROOT    = Path(__file__).parent.resolve()
BACKEND = ROOT / "backend"
VENV    = BACKEND / "venv"
IS_WIN  = sys.platform == "win32"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")
VENV_PIP= VENV / ("Scripts/pip.exe"    if IS_WIN else "bin/pip")

G = "\033[32m"; Y = "\033[33m"; R = "\033[31m"; B = "\033[34m"; NC = "\033[0m"; BOLD="\033[1m"
def ok(m):   print(f"  {G}✅ {m}{NC}")
def warn(m): print(f"  {Y}⚠️  {m}{NC}")
def fail(m): print(f"  {R}❌ {m}{NC}")
def info(m): print(f"  {B}ℹ️  {m}{NC}")
def head(m): print(f"\n{BOLD}{m}{NC}")

errors = []

# ── 1. Python ───────────────────────────────────────────────────────────────
head("1. Python")
v = sys.version_info
if v >= (3, 10):
    ok(f"Python {v.major}.{v.minor}.{v.micro}")
else:
    fail(f"Python {v.major}.{v.minor} — потрібен 3.10+")
    errors.append("python_version")
if v.minor == 13:
    warn("Python 3.13 — може бути несумісність з деякими пакетами")

# ── 2. Venv ─────────────────────────────────────────────────────────────────
head("2. Venv")
if VENV_PY.exists():
    ok(f"venv знайдено: {VENV_PY}")
else:
    fail(f"venv не знайдено: {VENV}")
    info("Запустіть: python start.py")
    errors.append("no_venv")

# ── 3. Залежності ────────────────────────────────────────────────────────────
head("3. Залежності")
packages = {
    "fastapi":          "fastapi",
    "uvicorn":          "uvicorn",
    "asyncpg":          "asyncpg",
    "sqlalchemy":       "sqlalchemy",
    "bcrypt":           "bcrypt",
    "jose":             "python-jose",
    "pydantic":         "pydantic",
    "pydantic_settings":"pydantic-settings",
}
if VENV_PY.exists():
    for mod, pkg in packages.items():
        r = subprocess.run(
            [str(VENV_PY), "-c", f"import {mod}; print({mod}.__version__ if hasattr({mod},'__version__') else 'ok')"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            ok(f"{pkg} ({r.stdout.strip()})")
        else:
            fail(f"{pkg} — НЕ встановлено")
            errors.append(f"missing_{pkg}")
else:
    warn("Пропускаємо — venv не існує")

# ── 4. .env ──────────────────────────────────────────────────────────────────
head("4. Конфігурація (.env)")
env_file = BACKEND / ".env"
env_cfg  = {}
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v2 = line.partition("=")
            env_cfg[k.strip()] = v2.strip().strip('"').strip("'")
    ok(f".env знайдено")
    info(f"DB_HOST     = {env_cfg.get('DB_HOST','(не задано)')}")
    info(f"DB_PORT     = {env_cfg.get('DB_PORT','(не задано)')}")
    info(f"DB_USER     = {env_cfg.get('DB_USER','(не задано)')}")
    info(f"DB_PASSWORD = {'*' * len(env_cfg.get('DB_PASSWORD',''))}")
    info(f"DB_NAME     = {env_cfg.get('DB_NAME','(не задано)')}")
    info(f"PORT        = {env_cfg.get('PORT','8000')}")
    info(f"FRONTEND_ORIGINS = {env_cfg.get('FRONTEND_ORIGINS','(не задано)')}")
    if env_cfg.get("FRONTEND_ORIGINS","") not in ("*", ""):
        if "localhost:3000" not in env_cfg.get("FRONTEND_ORIGINS",""):
            warn("FRONTEND_ORIGINS не містить http://localhost:3000")
            warn("→ Змініть на: FRONTEND_ORIGINS=*")
else:
    fail(".env не знайдено")
    info(f"Створіть: copy backend\\.env.example backend\\.env")
    errors.append("no_env")

# ── 5. PostgreSQL TCP ────────────────────────────────────────────────────────
head("5. PostgreSQL (TCP з'єднання)")
pg_host = env_cfg.get("DB_HOST", "localhost")
pg_port = int(env_cfg.get("DB_PORT", "5432"))
try:
    s = socket.create_connection((pg_host, pg_port), timeout=3)
    s.close()
    ok(f"PostgreSQL доступний на {pg_host}:{pg_port}")
except Exception as e:
    fail(f"Не вдалось з'єднатись з {pg_host}:{pg_port}: {e}")
    info("Перевірте що PostgreSQL сервіс запущено:")
    info("  Windows: services.msc → postgresql-x64-* → Запустити")
    errors.append("postgres_tcp")

# ── 6. asyncpg підключення ───────────────────────────────────────────────────
head("6. PostgreSQL (підключення до БД)")
if VENV_PY.exists() and "postgres_tcp" not in errors:
    db_user = env_cfg.get("DB_USER","postgres")
    db_pass = env_cfg.get("DB_PASSWORD","root")
    db_host = env_cfg.get("DB_HOST","localhost")
    db_port = env_cfg.get("DB_PORT","5432")
    db_name = env_cfg.get("DB_NAME","medipredictor")
    
    # Спробуємо підключитись через asyncpg
    test_script = f"""
import asyncio, asyncpg, sys
async def t():
    try:
        c = await asyncpg.connect('postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}')
        v = await c.fetchval('SELECT version()')
        await c.close()
        print('OK:' + v[:40])
    except Exception as e:
        print('ERR:' + str(e))
        sys.exit(1)
asyncio.run(t())
"""
    r = subprocess.run([str(VENV_PY), "-c", test_script],
                       capture_output=True, text=True, cwd=str(BACKEND))
    out = (r.stdout + r.stderr).strip()
    if out.startswith("OK:"):
        ok(f"Підключено до БД '{db_name}': {out[3:]}")
    else:
        fail(f"Помилка підключення до '{db_name}'")
        info(f"  {out}")
        if "does not exist" in out:
            info(f"  База '{db_name}' не існує — створіть її:")
            info(f"  У pgAdmin: правою кнопкою → Databases → Create")
        elif "password" in out.lower():
            info(f"  Невірний пароль. Перевірте DB_PASSWORD в backend\\.env")
        errors.append("postgres_auth")
else:
    warn("Пропускаємо — venv або TCP недоступні")

# ── 7. Порт 8000 ─────────────────────────────────────────────────────────────
head("7. Порт бекенду (8000)")
api_port = int(env_cfg.get("PORT","8000"))
try:
    s = socket.create_connection(("127.0.0.1", api_port), timeout=2)
    s.close()
    ok(f"Бекенд ВЖЕ запущено на порту {api_port}!")
    import urllib.request
    try:
        resp = urllib.request.urlopen(f"http://localhost:{api_port}/health", timeout=2)
        data = resp.read().decode()
        ok(f"/health відповідає: {data}")
    except Exception as he:
        warn(f"/health помилка: {he}")
except Exception:
    warn(f"Бекенд не запущено на порту {api_port}")
    info("Запустіть: python start.py  або  python start.py --skip-db")

# ── 8. Порт 3000 ─────────────────────────────────────────────────────────────
head("8. Порт фронтенду (3000)")
try:
    s = socket.create_connection(("127.0.0.1", 3000), timeout=2)
    s.close()
    ok("Фронтенд-сервер запущено на порту 3000")
except Exception:
    warn("Фронтенд-сервер не запущено (запустіть через start.py)")

# ── Підсумок ──────────────────────────────────────────────────────────────────
print(f"\n{BOLD}{'═'*50}{NC}")
if not errors:
    print(f"{G}{BOLD}✅ Все гаразд! Можна запускати:{NC}")
    print(f"   python start.py --skip-db")
else:
    print(f"{R}{BOLD}❌ Знайдено проблеми ({len(errors)}):{NC}")
    for e in errors:
        solutions = {
            "no_venv":       "python start.py",
            "no_env":        "copy backend\\.env.example backend\\.env",
            "postgres_tcp":  "Запустіть PostgreSQL сервіс (services.msc)",
            "postgres_auth": "Перевірте DB_PASSWORD в backend\\.env",
        }
        if e in solutions:
            print(f"  → {solutions[e]}")
print(f"{BOLD}{'═'*50}{NC}\n")
