"""Seed background presets untuk preview visual matching (BR-IMG-08).

image_url memakai CSS gradient string — pola yang sama dengan product.image_url
sehingga dapat dirender langsung oleh frontend tanpa file aset tambahan.
"""
from sqlalchemy.orm import Session as DBSession

from app.models.background_preset import BackgroundPreset


BACKGROUND_SEED = [
    {
        "background_name": "Studio Putih",
        "background_category": "STUDIO",
        "image_url": "linear-gradient(180deg, #FFFFFF 0%, #ECECEC 100%)",
    },
    {
        "background_name": "Krem Hangat",
        "background_category": "STUDIO",
        "image_url": "linear-gradient(180deg, #FBF4E8 0%, #E8D5BC 100%)",
    },
    {
        "background_name": "Sage Lembut",
        "background_category": "NATURAL",
        "image_url": "linear-gradient(180deg, #E7EEE4 0%, #B9C9B2 100%)",
    },
    {
        "background_name": "Terracotta",
        "background_category": "WARM",
        "image_url": "linear-gradient(180deg, #F4E0D4 0%, #CE8B68 100%)",
    },
    {
        "background_name": "Biru Pastel",
        "background_category": "COOL",
        "image_url": "linear-gradient(180deg, #E8EFF7 0%, #A9C3DE 100%)",
    },
    {
        "background_name": "Charcoal Elegan",
        "background_category": "DARK",
        "image_url": "linear-gradient(180deg, #4A4A4F 0%, #232328 100%)",
    },
]


def seed_backgrounds(db: DBSession) -> None:
    for entry in BACKGROUND_SEED:
        existing = (
            db.query(BackgroundPreset)
            .filter(BackgroundPreset.background_name == entry["background_name"])
            .first()
        )
        if existing:
            existing.background_category = entry["background_category"]
            existing.image_url = entry["image_url"]
            existing.is_active = True
        else:
            db.add(BackgroundPreset(**entry, is_active=True))
    db.commit()
