import os
import sys
import tempfile
from pathlib import Path

# Use isolated SQLite per test session - set BEFORE any app imports
TEST_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"
# Seed only the base hand-authored catalog in tests (exclude the large synthetic
# dataset produced by app.catalog_gen) so the suite stays fast and deterministic.
os.environ.setdefault("SEED_INCLUDE_GENERATED", "0")

# Ensure backend root on sys.path
backend_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(backend_root))

import pytest
from app.core.database import Base, engine, SessionLocal
from app import models  # noqa: F401


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
