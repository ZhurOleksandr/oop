#!/usr/bin/env python3
"""
run_frontend.py — Запуск ТІЛЬКИ HTTP-сервера фронтенду
http://localhost:3000

Використання:
    python run_frontend.py
"""
import sys, os, webbrowser, threading, time
from pathlib import Path
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT     = Path(__file__).parent.resolve()
FRONTEND = ROOT / "frontend"
PORT     = 3000

if not FRONTEND.exists() or not (FRONTEND / "index.html").exists():
    print(f"❌ frontend/index.html не знайдено: {FRONTEND}")
    sys.exit(1)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)
    def log_message(self, fmt, *args):
        pass
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

print(f"🌐 Фронтенд-сервер: http://localhost:{PORT}")
print(f"   Зупинити: Ctrl+C\n")

# Відкриваємо браузер через 1 сек
def _open():
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")
threading.Thread(target=_open, daemon=True).start()

server = HTTPServer(("0.0.0.0", PORT), Handler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n🛑 Зупинено")
