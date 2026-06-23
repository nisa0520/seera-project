"""Advanced synthetic catalog **data + image** generator (additive, isolated).

This package generates synthetic catalog entries (product + color metadata) and
their matching *reference-based* images (recolors of existing template assets),
plus derived ``ProductVisualAsset`` / ``ProductVtonAsset`` rows — fully compatible
with the existing seed system and **without modifying any existing business logic,
algorithm, or schema**.

Everything here is read-only with respect to the rest of the codebase: models and
``compute_color_features`` are imported but never mutated, and the existing seed
functions are extended only by *data* (more entries), never by a code-path change.

Entry point: ``python -m app.catalog_gen --help`` (see :mod:`app.catalog_gen.cli`).
"""

from app.catalog_gen.config import GenConfig

__all__ = ["GenConfig"]
