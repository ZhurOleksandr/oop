#!/usr/bin/env python3
"""
run_backend.py — Запуск ТІЛЬКИ бекенду (для діагностики)
Використання:  python run_backend.py
"""
import sys, os, subprocess
from pathlib import Path

ROOT    = Path(__file__).parent.resolve()
BACKEND = ROOT / "backend"
VENV    = BACKEND / "venv"
IS_WIN  = sys.platform == "win32"
VENV_PY = VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")
VENV_UV = VENV / ("Scripts/uvicorn.exe" if IS_WIN else "bin/uvicorn")

if not VENV_PY.exists():
    print("❌ venv не знайдено. Спочатку запустіть: python start.py")
    sys.exit(1)

if not (BACKEND / ".env").exists():
    print("❌ backend/.env не знайдено.")
    print("   Виконайте: copy backend\\.env.example backend\\.env")
    sys.exit(1)

if not (BACKEND / "main.py").exists():
    print(f"❌ backend/main.py не знайдено. Шлях: {BACKEND}")
    sys.exit(1)

print(f"📂 Робоча директорія: {BACKEND}")
print(f"🚀 Запускаємо FastAPI бекенд...")
print(f"   API:     http://localhost:8000")
print(f"   Swagger: http://localhost:8000/docs")
print(f"   Зупинити: Ctrl+C\n")

# Ключово: cwd=BACKEND — uvicorn знаходить main.py
subprocess.run(
    [str(VENV_UV), "main:app",
     "--host", "0.0.0.0",
     "--port", "8000",
     "--reload",
     "--log-level", "info"],
    cwd=str(BACKEND)   # ← робоча директорія = backend/
)
