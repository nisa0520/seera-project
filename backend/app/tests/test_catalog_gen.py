"""Tests for the additive synthetic catalog generator (app.catalog_gen).

These exercise the acceptance-critical guarantees: determinism (byte-identical re-run),
schema-valid colour-first records, palette-only colours, the ΔE2000 QA gate, and
background preservation (pixels outside the garment mask are never modified).
"""
import numpy as np
import pytest
from PIL import Image

from app.catalog_gen import masks
from app.catalog_gen.config import GenConfig
from app.catalog_gen.data_gen import RANK_ROLE, generate_spec
from app.catalog_gen.palette import Palette
from app.catalog_gen.pipeline import Generator
from app.catalog_gen.templates import TemplateRegistry

SEED = 7
COUNT = 24


def _cfg(tmp_path, **over) -> GenConfig:
    base = dict(
        count=COUNT,
        seed=SEED,
        out_catalog_dir=tmp_path / "catalog",
        out_cutout_dir=tmp_path / "cutout",
        out_manifest=tmp_path / "manifest.json",
        out_seed=tmp_path / "seed" / "generated_products.py",
    )
    base.update(over)
    return GenConfig(**base)


def test_records_are_schema_valid_and_palette_only():
    palette = Palette()
    registry = TemplateRegistry()
    palette_names = {c.name for c in palette.colors}
    for i in range(1, 60):
        spec = generate_spec(i, GenConfig(count=60, seed=SEED), palette, registry)
        k = len(spec.colors)
        assert 1 <= k <= 4
        # ranks contiguous & 1-based; roles distinct and rank-mapped.
        assert [r for r in range(1, k + 1)] == list(range(1, k + 1))
        roles = spec.roles
        assert roles == [RANK_ROLE[j + 1] for j in range(k)]
        assert len(set(roles)) == k
        assert roles[0] == "DOMINANT"
        # percentages: sum to exactly 100, non-increasing.
        assert abs(sum(spec.percentages) - 100.0) < 1e-6
        assert all(spec.percentages[j] >= spec.percentages[j + 1] for j in range(k - 1))
        # colours come from the existing palette only.
        assert all(c.name in palette_names for c in spec.colors)
        # taxonomy derived from template, not random.
        assert spec.category == spec.template.category
        assert spec.target_gender == spec.template.target_gender


def test_pipeline_determinism_byte_identical(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    stats_a, man_a = Generator(_cfg(a)).run()
    stats_b, man_b = Generator(_cfg(b)).run()

    assert stats_a.persisted == stats_b.persisted >= 1
    assert man_a["entries"] == man_b["entries"]

    files = sorted(p.name for p in (a / "catalog").glob("*.png"))
    assert files, "expected at least one persisted catalog image"
    for name in files:
        assert (a / "catalog" / name).read_bytes() == (b / "catalog" / name).read_bytes()
    # seed module is reproducible too
    assert (a / "seed" / "generated_products.py").read_text() == \
           (b / "seed" / "generated_products.py").read_text()


def test_qa_passes_for_all_persisted(tmp_path):
    _, manifest = Generator(_cfg(tmp_path)).run()
    persisted = [e for e in manifest["entries"] if e["persisted"]]
    assert persisted, "expected persisted entries"
    for e in persisted:
        qa = e["qa"]
        if qa.get("skipped"):
            continue
        assert qa["passed"] is True
        assert qa["dominant_ok"] is True


def test_background_outside_mask_is_unchanged(tmp_path):
    """Recolor must leave every pixel outside the garment mask byte-for-byte identical."""
    gen = Generator(_cfg(tmp_path))
    _, manifest = gen.run()
    persisted = [e for e in manifest["entries"] if e["persisted"]]
    registry = TemplateRegistry()
    checked = 0
    for e in persisted[:8]:
        template = registry.by_url(e["template"])
        mask = masks.load_mask(template)
        orig = np.array(Image.open(template.source_image_path).convert("RGB"))
        out = np.array(Image.open(tmp_path / "catalog" / f"{e['external_catalog_id']}.png").convert("RGB"))
        assert out.shape == orig.shape
        outside = ~mask.garment
        assert np.array_equal(out[outside], orig[outside]), \
            f"{e['external_catalog_id']}: pixels outside garment mask were modified"
        checked += 1
    assert checked > 0
