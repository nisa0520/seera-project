"""Run all seeders. Usage: python -m app.seed.run_seed"""
from app.core.database import SessionLocal, Base, engine
from app.core.logging import logger
from app import models  # noqa: F401  - register models

from app.seed.seed_aiml_categories import seed_aiml
from app.seed.seed_education import seed_education
from app.seed.seed_catalog_dummy import seed_catalog


def run() -> None:
    logger.info("Creating tables (if missing)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        logger.info("Seeding AIML categories...")
        seed_aiml(db)
        logger.info("Seeding education topics & contents...")
        seed_education(db)
        logger.info("Seeding categories, colors, and products...")
        seed_catalog(db)
        logger.info("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
