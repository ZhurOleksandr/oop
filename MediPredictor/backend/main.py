# backend/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from middleware import RequestTimingMiddleware, SecurityHeadersMiddleware, AuditLogMiddleware
from routers import auth, users, patients, algorithms, analyses, stats

logger = logging.getLogger("medipredictor")
settings = get_settings()

app = FastAPI(
    title="MediPredictor API",
    description=(
        "Система прогнозування та аналізу захворювань.\n\n"
        "**Авторизація:** POST /api/auth/login → Bearer token"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
origins = settings.cors_origins
allow_all = origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://localhost:\d+" if allow_all else None,
    allow_credentials=not allow_all,  # credentials несумісні з allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Інші middleware ───────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestTimingMiddleware, slow_threshold_ms=800)
app.add_middleware(AuditLogMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(patients.router)
app.include_router(algorithms.router)
app.include_router(analyses.router)
app.include_router(stats.router)


@app.on_event("startup")
async def on_startup():
    logger.info(
        "MediPredictor API v2.0  →  http://localhost:%d/docs", settings.PORT
    )
    logger.info(
        "DB: %s:%d/%s (user: %s)", settings.DB_HOST, settings.DB_PORT,
        settings.DB_NAME, settings.DB_USER
    )
    logger.info("CORS origins: %s", settings.FRONTEND_ORIGINS)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/", tags=["meta"])
async def root():
    return {"app": "MediPredictor API", "version": "2.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
