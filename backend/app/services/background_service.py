"""Background preset untuk preview visual matching (FR-IMG-12, BR-IMG-08)."""
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.background_preset import BackgroundPreset


class BackgroundService:
    def __init__(self, db: DBSession):
        self.db = db

    def list_active(self) -> list[BackgroundPreset]:
        return (
            self.db.query(BackgroundPreset)
            .filter(BackgroundPreset.is_active.is_(True))
            .order_by(BackgroundPreset.id)
            .all()
        )

    def get_active(self, background_id: int) -> Optional[BackgroundPreset]:
        return (
            self.db.query(BackgroundPreset)
            .filter(
                BackgroundPreset.id == background_id,
                BackgroundPreset.is_active.is_(True),
            )
            .first()
        )

    @staticmethod
    def serialize(preset: BackgroundPreset) -> dict:
        return {
            "background_id": preset.id,
            "background_name": preset.background_name,
            "background_category": preset.background_category,
            "image_url": preset.image_url,
        }
