# 🪟 Налаштування на Windows

## Проблема

При встановленні залежностей може виникнути помилка:
```
Failed to build wheel for pydantic-core / asyncpg
Caused by: Failed to build a native library through cargo
```

**Причина:** Ці пакети потребують компілятора Rust, якого немає на Windows за замовчуванням.

**Рішення:** Оновлений `requirements.txt` використовує версії з готовими Windows-wheels.

---

## ✅ Крок 1 — Встановити Python (якщо не встановлено)

1. Завантажте **Python 3.11** з https://www.python.org/downloads/
2. При встановленні **обов'язково** поставте ✅ `Add Python to PATH`
3. Перевірте: відкрийте `cmd` і введіть `python --version`

> ⚠️ Python 3.13 поки що не підтримується деякими пакетами. Використовуйте **3.10, 3.11 або 3.12**.

---

## ✅ Крок 2 — Встановити PostgreSQL

1. Завантажте PostgreSQL 16 з https://www.postgresql.org/download/windows/
2. При встановленні запам'ятайте пароль суперюзера `postgres`
3. Залиште порт `5432` (за замовчуванням)
4. Після встановлення додайте до PATH:
   - Відкрийте **Параметри системи** → **Змінні середовища**
   - До змінної `Path` додайте: `C:\Program Files\PostgreSQL\16\bin`
5. Перевірте: `psql --version`

---

## ✅ Крок 3 — Запустити систему

**Варіант A — через .bat файл (найпростіше):**
```
Двічі клікніть на start.bat
```

**Варіант B — через PowerShell:**
```powershell
cd D:\MediPredictor
python start.py
```

**Варіант C — вручну:**
```cmd
cd D:\MediPredictor\backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install --only-binary pydantic-core --only-binary asyncpg -r requirements.txt
copy .env.example .env
cd ..
python start.py --skip-db
```

---

## 🔧 Якщо залежності все одно не встановлюються

```cmd
pip install --upgrade pip setuptools wheel
pip install pydantic==2.10.3 --only-binary pydantic-core
pip install asyncpg==0.30.0 --only-binary asyncpg
pip install fastapi uvicorn[standard] passlib[bcrypt] python-jose[cryptography]
pip install sqlalchemy python-multipart python-dotenv pydantic-settings
```

---

## 🛢️ Налаштування PostgreSQL вручну

Відкрийте **pgAdmin** або **psql** і виконайте:

```sql
CREATE USER mediuser WITH PASSWORD 'medipassword';
CREATE DATABASE medipredictor OWNER mediuser;
GRANT ALL PRIVILEGES ON DATABASE medipredictor TO mediuser;
```

Потім застосуйте схему:
```cmd
psql -U mediuser -h localhost -d medipredictor -f database\schema.sql
```
Пароль: `medipassword`

Потім ініціалізуйте дані:
```cmd
cd backend
venv\Scripts\python.exe init_db.py
```

---

## 🌐 Фронтенд

Після запуску серверу відкрийте у браузері:
```
frontend\index.html
```
(або браузер відкриється автоматично)

Якщо бекенд не запущено — система працює в **офлайн-режимі** (жовта смужка вгорі).

---

## 🔐 Акаунти

| Роль | Логін | Пароль |
|------|-------|--------|
| 🩺 Лікар | `doctor1` | `password123` |
| ⚙️ Адмін | `admin` | `admin123` |
| 📊 Аналітик | `analyst` | `analyst123` |

---

## ❓ Часті помилки

| Помилка | Рішення |
|---------|---------|
| `python не розпізнано` | Встановити Python з галочкою "Add to PATH" |
| `psql не розпізнано` | Додати `C:\Program Files\PostgreSQL\16\bin` до PATH |
| `Could not connect to server` | Запустити службу PostgreSQL: `services.msc` → PostgreSQL |
| `wheel for pydantic-core` | Використовуйте Python 3.10-3.12, не 3.13 |
| `cargo` / `maturin` помилка | pip install не знайшов pre-built wheel — перевірте версію Python |
