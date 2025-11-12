# shadowgate_api/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from shadowgate_api.db import Base, engine
from shadowgate_api.routers import users, admin
# Uncomment when these routers are ready and deployed
# from shadowgate_api.routers import loans, trades
from shadowgate_api.routers import loan_eligibility as elig
from fastapi import FastAPI
app = FastAPI(title="Shadowgate API")


MODELS_SQL = Path(__file__).with_name("models.sql")

# CORS (loose for dev; tighten to your domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _apply_models_sql():
    """Execute models.sql one statement at a time (Postgres-safe)."""
    if not MODELS_SQL.exists():
        print("[db] models.sql not found; skipping")
        return

    raw = MODELS_SQL.read_text(encoding="utf-8")
    # naive splitter is fine because the file only has simple CREATE/INDEX statements
    statements = [s.strip() for s in raw.split(";") if s.strip()]
    if not statements:
        print("[db] models.sql empty; skipping")
        return

    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)
    print(f"[db] models.sql applied ({len(statements)} statements)")

@app.on_event("startup")
def init_db_on_startup():
    # 1) Apply raw DDL
    _apply_models_sql()
    # 2) Create any ORM tables (if you add SQLAlchemy models later)
    Base.metadata.create_all(bind=engine)
    print("[db] ORM models created")

@app.get("/")
def root():
    return {"message": "Shadowgate API running"}

# Routers
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(elig.router)
# app.include_router(loans.router)
# app.include_router(trades.router)
