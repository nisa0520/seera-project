"""Database migration helpers for startup tasks."""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.core.database import engine
from app.core.logging import logger


BASE_REVISION = "0001_initial"
HEAD_REVISION = "head"


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.attributes["skip_logging_config"] = True
    return config


def _has_column(table_names: set[str], table: str, column: str) -> bool:
    if table not in table_names:
        return False
    inspector = inspect(engine)
    return column in {item["name"] for item in inspector.get_columns(table)}


def _has_gender_schema(table_names: set[str]) -> bool:
    return (
        _has_column(table_names, "users", "gender")
        and _has_column(table_names, "sessions", "gender_snapshot")
        and _has_column(table_names, "products", "target_gender")
    )


def ensure_schema_current() -> None:
    """Run Alembic migrations, including legacy DBs created before Alembic stamps."""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    config = _alembic_config()

    if "alembic_version" not in table_names:
        if table_names and _has_gender_schema(table_names):
            logger.info("Existing schema already has latest gender columns; stamping Alembic head.")
            command.stamp(config, HEAD_REVISION)
            return

        if table_names:
            logger.info("Existing pre-Alembic schema detected; stamping initial revision.")
            command.stamp(config, BASE_REVISION)

    logger.info("Applying database migrations...")
    command.upgrade(config, HEAD_REVISION)
