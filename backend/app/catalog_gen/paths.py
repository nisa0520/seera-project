"""Centralised, deterministic path resolution for the catalog generator.

All output locations are chosen so that the **existing** URL helpers resolve to
them with no logic change:

* catalog PNG   -> ``public/generated/<id>.png``                (served at ``/generated/<id>.png`` == ``image_url``)
* try-on cutout -> ``public/tryon/generated/<id>.png``          (== ``_cutout_url(image_url)``)
* VTON garment  -> ``backend/static/vton_garments/<id>.png``    (== ``_garment_url(image_url)``, which flattens to basename)

The generator never touches existing static assets; everything new lives under a
``/generated/`` prefix (or, for VTON garments, a uniquely-named ``GEN-*`` file).
"""
from __future__ import annotations

from pathlib import Path

# .../backend/app/catalog_gen/paths.py -> parents: [catalog_gen, app, backend, repo_root]
_THIS = Path(__file__).resolve()
BACKEND_DIR = _THIS.parents[2]
REPO_ROOT = _THIS.parents[3]

PUBLIC_DIR = REPO_ROOT / "public"

# Image-out roots (defaults; overridable via GenConfig).
DEFAULT_CATALOG_DIR = PUBLIC_DIR / "generated"
DEFAULT_CUTOUT_DIR = PUBLIC_DIR / "tryon" / "generated"
DEFAULT_GARMENT_DIR = BACKEND_DIR / "static" / "vton_garments"

# Existing template assets live directly under public/ and public/tryon/.
TEMPLATE_IMAGE_DIR = PUBLIC_DIR
TEMPLATE_CUTOUT_DIR = PUBLIC_DIR / "tryon"

# Static, hand-/offline-authored labeled region masks (computed once, cached).
MASK_CACHE_DIR = _THIS.parent / "mask_cache"

# Default build artefacts.
DEFAULT_MANIFEST = REPO_ROOT / "build" / "generated_manifest.json"
DEFAULT_SEED_OUT = BACKEND_DIR / "app" / "seed" / "generated" / "generated_products.py"


def url_to_template_image(image_url: str) -> Path:
    """Map a template catalog ``image_url`` (e.g. ``/koko-putih.png``) to disk."""
    return TEMPLATE_IMAGE_DIR / image_url.lstrip("/")


def url_to_template_cutout(image_url: str) -> Path:
    """Map a template ``image_url`` to its preprocessed transparent cutout."""
    return TEMPLATE_CUTOUT_DIR / image_url.lstrip("/")
