"""Derive the catalog image URL for a generated product."""
from __future__ import annotations


def catalog_url(external_catalog_id: str) -> str:
    """The catalog ``image_url`` (served from ``public/generated/``)."""
    return f"/generated/{external_catalog_id}.png"
