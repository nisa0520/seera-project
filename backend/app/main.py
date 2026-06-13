from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import logger
from app.api.v1.router import api_router

# Ensure models are registered
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} (env={settings.APP_ENV})")
    # Auto-create tables when DB is empty (helpful for dev/SQLite); Alembic still authoritative for migrations
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        logger.warning(f"create_all skipped due to: {exc}")
    yield
    logger.info("Shutting down")


app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "docs": "/docs", "health": "/health"}
