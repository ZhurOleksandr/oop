#!/usr/bin/env python3
"""
start.py — Єдина точка запуску MediPredictor v2.0

  http://localhost:3000  →  фронтенд (frontend/index.html)
  http://localhost:8000  →  FastAPI API + Swagger (/docs)

Використання:
    python start.py
    python start.py --skip-db      пропустити ініціалізацію БД
    python start.py --no-browser   не відкривати браузер автоматично
"""
import sys
import os
import subprocess
import argparse
import platform
import threading
import time
import webbrowser
import re
from pathlib import Path
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ── Кольори ─────────────────────────────────────────────────────────────────
RED = "\033[0;31m"; GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"; BOLD = "\033[1m"; NC = "\033[0m"

def ok(m):   print(f"{GREEN}✅ {m}{NC}")
def warn(m): print(f"{YELLOW}⚠️  {m}{NC}")
def err(m):  print(f"{RED}❌ {m}{NC}"); sys.exit(1)
def info(m): print(f"{BLUE}ℹ️  {m}{NC}")
def head(m): print(f"\n{BOLD}{m}{NC}")

IS_WIN  = platform.system() == "Windows"
ROOT    = Path(__file__).parent.resolve()
BACKEND = ROOT / "backend"
FRONTEND= ROOT / "frontend"
VENV    = BACKEND / "venv"

if IS_WIN:
    VENV_PY  = VENV / "Scripts" / "python.exe"
    VENV_PIP = VENV / "Scripts" / "pip.exe"
    VENV_UV  = VENV / "Scripts" / "uvicorn.exe"
else:
    VENV_PY  = VENV / "bin" / "python"
    VENV_PIP = VENV / "bin" / "pip"
    VENV_UV  = VENV / "bin" / "uvicorn"

FRONTEND_PORT = 3000
BACKEND_PORT  = 8000


# ════════════════════════════════════════════════════════════════════════════
# Читання .env без зовнішніх бібліотек
# ════════════════════════════════════════════════════════════════════════════

def read_dotenv(path: Path) -> dict:
    """Читає .env файл у словник без python-dotenv."""
    result = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def get_db_config() -> dict:
    """Повертає конфігурацію БД з backend/.env."""
    env = read_dotenv(BACKEND / ".env")

    # Якщо є повний DATABASE_URL — парсимо
    url = env.get("DATABASE_URL", "")
    if url.startswith("postgresql"):
        m = re.match(
            r"postgresql(?:\+asyncpg)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)", url
        )
        if m:
            return {
                "user": m.group(1), "password": m.group(2),
                "host": m.group(3), "port": int(m.group(4)),
                "dbname": m.group(5),
            }

    return {
        "host":     env.get("DB_HOST",     "localhost"),
        "port":     int(env.get("DB_PORT", "5432")),
        "user":     env.get("DB_USER",     "postgres"),
        "password": env.get("DB_PASSWORD", "root"),
        "dbname":   env.get("DB_NAME",     "medipredictor"),
    }


# ════════════════════════════════════════════════════════════════════════════
# КРОК 1 — Python
# ════════════════════════════════════════════════════════════════════════════

def check_python():
    head("1. Перевірка Python")
    v = sys.version_info
    info(f"Python {v.major}.{v.minor}.{v.micro} | {platform.system()}")
    if v.major < 3 or (v.major == 3 and v.minor < 10):
        err("Потрібен Python 3.10+. Завантажте: https://www.python.org/downloads/")
    if v.minor == 13:
        warn("Python 3.13 — рекомендовано 3.11 або 3.12 для кращої сумісності.")
    ok(f"Python {v.major}.{v.minor} — OK")


# ════════════════════════════════════════════════════════════════════════════
# КРОК 2 — Venv
# ════════════════════════════════════════════════════════════════════════════

def setup_venv():
    head("2. Віртуальне середовище")
    if VENV_PY.exists():
        ok("venv вже існує")
        return
    info("Створюємо venv...")
    r = subprocess.run(
        [sys.executable, "-m", "venv", str(VENV)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        err(f"Помилка venv:\n{r.stderr}")
    ok("venv створено")


# ════════════════════════════════════════════════════════════════════════════
# КРОК 3 — Залежності
# ════════════════════════════════════════════════════════════════════════════

def install_deps():
    head("3. Встановлення залежностей")
    req = BACKEND / "requirements.txt"
    if not req.exists():
        err(f"requirements.txt не знайдено: {req}")

    subprocess.run(
        [str(VENV_PIP), "install", "--upgrade", "pip", "setuptools", "wheel"],
        capture_output=True
    )

    info("pip install -r requirements.txt ...")
    r = subprocess.run(
        [str(VENV_PIP), "install",
         "--only-binary", "pydantic-core",
         "--only-binary", "asyncpg",
         "--only-binary", "cryptography",
         "-r", str(req)],
        cwd=str(BACKEND)
    )
    if r.returncode != 0:
        warn("Спроба без --only-binary...")
        r2 = subprocess.run(
            [str(VENV_PIP), "install", "-r", str(req)],
            cwd=str(BACKEND)
        )
        if r2.returncode != 0:
            warn(f"Не всі пакети встановились. Спробуйте вручну:")
            warn(f"  {VENV_PIP} install -r backend/requirements.txt")
            err("Встановлення не вдалося")

    ok("Залежності встановлено")


# ════════════════════════════════════════════════════════════════════════════
# КРОК 4 — .env
# ════════════════════════════════════════════════════════════════════════════

def setup_env():
    head("4. Конфігурація (.env)")
    env_file    = BACKEND / ".env"
    env_example = BACKEND / ".env.example"

    if env_file.exists():
        cfg = read_dotenv(env_file)
        host = cfg.get("DB_HOST", "localhost")
        user = cfg.get("DB_USER", "postgres")
        dbname = cfg.get("DB_NAME", "medipredictor")
        ok(f".env знайдено  (БД: {user}@{host}/{dbname})")
        return

    import secrets
    secret = secrets.token_hex(32)

    if env_example.exists():
        content = env_example.read_text(encoding="utf-8")
        content = content.replace(
            "change_me_to_a_long_random_string_minimum_32_characters",
            secret
        )
    else:
        content = (
            f"DB_HOST=localhost\nDB_PORT=5432\nDB_USER=postgres\n"
            f"DB_PASSWORD=root\nDB_NAME=medipredictor\n\n"
            f"SECRET_KEY={secret}\nALGORITHM=HS256\n"
            f"ACCESS_TOKEN_EXPIRE_MINUTES=480\n"
            f"FRONTEND_ORIGINS=http://localhost:{FRONTEND_PORT},"
            f"http://localhost:5500,http://127.0.0.1:5500\n"
            f"HOST=0.0.0.0\nPORT={BACKEND_PORT}\n"
        )

    env_file.write_text(content, encoding="utf-8")
    ok(".env створено")
    warn("Відкрийте backend\\.env і вкажіть ваш DB_PASSWORD!")


# ════════════════════════════════════════════════════════════════════════════
# КРОК 5 — Ініціалізація БД
# ════════════════════════════════════════════════════════════════════════════

def init_database():
    head("5. Ініціалізація бази даних")

    cfg = get_db_config()
    info(f"БД: {cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}")

    script = BACKEND / "init_db.py"
    if not script.exists():
        warn("init_db.py не знайдено — пропускаємо")
        return

    r = subprocess.run([str(VENV_PY), str(script)], cwd=str(BACKEND))
    if r.returncode != 0:
        print()
        warn("Ініціалізація БД завершилась з помилкою.")
        warn("Перевірте:")
        warn(f"  1. PostgreSQL сервіс запущено")
        warn(f"  2. Налаштування в backend\\.env")
        warn(f"  3. База '{cfg['dbname']}' існує")
        warn("Ручний запуск: cd backend && python init_db.py")
    else:
        ok("БД ініціалізовано")


# ════════════════════════════════════════════════════════════════════════════
# КРОК 6 — HTTP-сервер фронтенду
#
# КЛЮЧОВЕ ВИПРАВЛЕННЯ: передаємо directory= в обробник явно,
# тому os.chdir() для бекенду НЕ впливає на те, що роздає фронтенд.
# ════════════════════════════════════════════════════════════════════════════

class FrontendHandler(SimpleHTTPRequestHandler):
    """
    HTTP-обробник що завжди роздає файли з папки FRONTEND,
    незалежно від поточного робочого каталогу процесу.
    """

    def __init__(self, *args, directory: str = str(FRONTEND), **kwargs):
        # directory передається явно — не залежить від os.getcwd()
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        pass  # Без зайвих логів у консоль

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store")
        super().end_headers()


def start_frontend_server() -> HTTPServer | None:
    """Запускає HTTP-сервер фронтенду в окремому фоновому потоці."""
    if not FRONTEND.exists():
        warn(f"Папка frontend не знайдена: {FRONTEND}")
        return None

    if not (FRONTEND / "index.html").exists():
        warn(f"frontend/index.html не знайдено")
        return None

    # Передаємо FRONTEND папку через partial — фіксуємо directory
    handler = partial(FrontendHandler, directory=str(FRONTEND))

    try:
        server = HTTPServer(("0.0.0.0", FRONTEND_PORT), handler)
    except OSError as e:
        if e.errno in (98, 10048):  # Address already in use (Linux/Windows)
            warn(f"Порт {FRONTEND_PORT} вже зайнятий.")
            warn(f"Можливо фронтенд вже запущено: http://localhost:{FRONTEND_PORT}")
        else:
            warn(f"Не вдалось запустити HTTP-сервер фронтенду: {e}")
        return None

    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


# ════════════════════════════════════════════════════════════════════════════
# КРОК 7 — Запуск бекенду + вивід інформації
# ════════════════════════════════════════════════════════════════════════════

def start_all(no_browser: bool = False):
    head("Запуск серверів")

    env_cfg = read_dotenv(BACKEND / ".env")
    backend_port = int(env_cfg.get("PORT", BACKEND_PORT))

    # Перевіряємо що localhost:3000 є в CORS
    origins = env_cfg.get("FRONTEND_ORIGINS", "")
    if f"http://localhost:{FRONTEND_PORT}" not in origins:
        env_path = BACKEND / ".env"
        new_origins = (
            f"http://localhost:{FRONTEND_PORT},"
            + origins if origins else f"http://localhost:{FRONTEND_PORT}"
        )
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
            new_lines = [
                f"FRONTEND_ORIGINS={new_origins}"
                if l.startswith("FRONTEND_ORIGINS=") else l
                for l in lines
            ]
            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # Запускаємо фронтенд HTTP-сервер
    fe_server = start_frontend_server()

    print()
    print(f"{BOLD}{'═' * 56}{NC}")
    print(f"{GREEN}{BOLD}   🚀 MediPredictor запущено!{NC}")
    print(f"{BOLD}{'═' * 56}{NC}")
    print()
    if fe_server:
        print(f"  {BOLD}🌐 Фронтенд:{NC}  {BLUE}http://localhost:{FRONTEND_PORT}{NC}")
    else:
        print(f"  {YELLOW}⚠️  Фронтенд-сервер не запустився{NC}")
    print(f"  {BOLD}🔌 API:{NC}       {BLUE}http://localhost:{backend_port}{NC}")
    print(f"  {BOLD}📖 Swagger:{NC}   {BLUE}http://localhost:{backend_port}/docs{NC}")
    print()
    print(f"  {BOLD}Акаунти:{NC}")
    print(f"    🩺 doctor1  / password123")
    print(f"    ⚙️  admin    / admin123")
    print(f"    📊 analyst  / analyst123")
    print()
    print(f"  {YELLOW}Зупинити: Ctrl+C{NC}")
    print()

    # Відкриваємо браузер через 1.5 сек
    if not no_browser and fe_server:
        def _open():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
        threading.Thread(target=_open, daemon=True).start()

    # Запускаємо бекенд (НЕ міняємо cwd через os.chdir — передаємо cwd= напряму)
    subprocess.run(
        [str(VENV_UV), "main:app",
         "--host", "0.0.0.0",
         "--port", str(backend_port),
         "--reload",
         "--log-level", "info"],
        cwd=str(BACKEND)   # ← uvicorn запускається в backend/, але os.getcwd() НЕ змінюється
    )


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="MediPredictor v2.0")
    parser.add_argument("--skip-db",    action="store_true", help="Пропустити ініціалізацію БД")
    parser.add_argument("--no-browser", action="store_true", help="Не відкривати браузер")
    parser.add_argument("--check",      action="store_true", help="Тільки перевірка оточення")
    args = parser.parse_args()

    print(f"\n{BOLD}{'═' * 56}{NC}")
    print(f"{BOLD}   🏥 MediPredictor v2.0 — Система запуску{NC}")
    print(f"{BOLD}{'═' * 56}{NC}")

    check_python()
    setup_venv()
    install_deps()
    setup_env()

    if not args.skip_db:
        init_database()
    else:
        info("Пропускаємо ініціалізацію БД (--skip-db)")

    if args.check:
        print()
        ok("Перевірка завершена. Запустіть: python start.py")
        return

    start_all(no_browser=args.no_browser)


if __name__ == "__main__":
    main()
