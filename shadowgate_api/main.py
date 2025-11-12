# shadowgate_api/main.py
from fastapi import FastAPI

from shadowgate_api.db import Base, engine
from shadowgate_api.routers import users, admin
# from shadowgate_api.routers import trades, loans  # enable when ready
from shadowgate_api.routers import users, admin, loans, trades
from shadowgate_api.routers import loan_eligibility as elig
from pathlib import Path
from sqlalchemy import text
from shadowgate_api.db import engine  # your existing engine

MODELS_SQL = Path(__file__).with_name("models.sql")




app = FastAPI(title="Shadowgate API")

# --- CORS: allow browser calls from any site (dev-friendly). Tighten later. ---
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # loosen for testing; tighten later to your domain(s)
    allow_credentials=False,    # you're not using cookies/sessions
    allow_methods=["*"],        # POST/GET/OPTIONS etc.
    allow_headers=["*"],        # Content-Type, Authorization, etc.
)

@app.on_event("startup")
def init_db_on_startup():
    # 1. Run raw SQL setup if available
    if MODELS_SQL.exists():
        sql = MODELS_SQL.read_text(encoding="utf-8")
        with engine.begin() as conn:
            conn.exec_driver_sql(sql)
        print("[db] models.sql applied")
    else:
        print("[db] models.sql not found; skipping")

    # 2. Ensure ORM models are created
    Base.metadata.create_all(bind=engine)
    print("[db] ORM models created")


# --- Health check ---
@app.get("/")
def root():
    return {"message": "Shadowgate API running"}

# --- Routers ---
app.include_router(users.router)   # /api/...
app.include_router(admin.router)   # /api/admin/...
app.include_router(elig.router)
# app.include_router(trades.router)
# app.include_router(loans.router)
