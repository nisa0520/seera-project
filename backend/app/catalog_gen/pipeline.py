"""End-to-end generation pipeline (per-product, deterministic, idempotent).

For each product: derive a stable seed -> generate colour-first metadata -> load the
template image + cached masks -> partition the garment by percentage -> CIELAB recolor
-> emit the three consistent artifacts -> run the ΔE2000 QA gate (with a small
deterministic retry budget). Only QA-passing entries are persisted; failures are
recorded in the manifest and skipped. Re-running overwrites the same image paths and
re-emits identical records, so the dataset is reproducible and duplicate-free.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image

from app.catalog_gen import assets, emit, masks, recolor
from app.catalog_gen.config import GenConfig
from app.catalog_gen.data_gen import ProductSpec, generate_spec
from app.catalog_gen.masks import TemplateMask
from app.catalog_gen.palette import Palette
from app.catalog_gen.qa import run_qa
from app.catalog_gen.rng import Deterministic
from app.catalog_gen.templates import Template, TemplateRegistry

# Texture strength per QA attempt: start fully textured, then tighten *decisively* on
# retries. For near-neutral colours that differ mainly in lightness, a wide L-texture
# spread makes KMeans area shares seed-sensitive; collapsing it (<=0.15) yields a clean,
# seed-independent separation. Most products pass at full texture; only hard close-L
# pairs fall through to the tight end. All steps are deterministic.
_RETRY_TEXTURE = [1.0, 0.5, 0.2, 0.1, 0.05]


@dataclass
class RunStats:
    requested: int = 0
    persisted: int = 0
    failed: int = 0
    failures: List[dict] = field(default_factory=list)


def _save_png(arr: np.ndarray, path: Path) -> None:
    # Mode is inferred from the array shape (HxWx3 -> RGB, HxWx4 -> RGBA), so output is
    # deterministic and we avoid Pillow's deprecated explicit-mode path.
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(path, format="PNG", compress_level=6)


class Generator:
    def __init__(self, cfg: GenConfig):
        self.cfg = cfg
        self.palette = Palette()
        self.registry = TemplateRegistry(cfg.limit_templates)
        self._img_cache: Dict[str, np.ndarray] = {}
        self._mask_cache: Dict[str, TemplateMask] = {}

    # -- template resources (loaded once, reused for every variant) --------------- #
    def _template_rgb(self, t: Template) -> np.ndarray:
        if t.image_url not in self._img_cache:
            self._img_cache[t.image_url] = np.array(
                Image.open(t.source_image_path).convert("RGB")
            )
        return self._img_cache[t.image_url]

    def _template_mask(self, t: Template) -> TemplateMask:
        if t.image_url not in self._mask_cache:
            self._mask_cache[t.image_url] = masks.load_mask(t)
        return self._mask_cache[t.image_url]

    # -- per-product render + QA -------------------------------------------------- #
    def _render_and_qa(self, spec: ProductSpec):
        t = spec.template
        rgb = self._template_rgb(t)
        mask = self._template_mask(t)
        targets = [c.lab for c in spec.colors]
        names = [c.name for c in spec.colors]
        det = Deterministic(spec.external_catalog_id, salt=self.cfg.seed)

        last = None
        budget = max(1, self.cfg.qa_retry_budget + 1)
        for attempt in range(budget):
            ts = _RETRY_TEXTURE[min(attempt, len(_RETRY_TEXTURE) - 1)]
            cat, subj, _ = recolor.render_artifacts(rgb, mask, spec.percentages, targets, ts)
            if not self.cfg.qa_enabled:
                return cat, subj, None, True
            qa = run_qa(
                cat, mask.garment, names, targets, spec.percentages,
                seed=det.seed("qa") + attempt,
                area_tolerance_pp=self.cfg.qa_area_tolerance_pp,
                delta_e_threshold=self.cfg.qa_delta_e_threshold,
                sample_cap=self.cfg.qa_sample_cap,
            )
            last = (cat, subj, qa)
            if qa.passed:
                return cat, subj, qa, True
        cat, subj, qa = last
        return cat, subj, qa, False

    # -- persistence -------------------------------------------------------------- #
    def _persist_images(self, spec: ProductSpec, cat: np.ndarray, subj: np.ndarray) -> None:
        ext = spec.external_catalog_id
        _save_png(cat, self.cfg.out_catalog_dir / f"{ext}.png")
        _save_png(subj, self.cfg.out_cutout_dir / f"{ext}.png")
        if assets.supports_vton_garment(spec):
            _save_png(subj, self.cfg.out_garment_dir / f"{ext}.png")

    def _seed_record(self, spec: ProductSpec) -> dict:
        return {
            "external_catalog_id": spec.external_catalog_id,
            "name": spec.name,
            "price": spec.price,
            "rating": spec.rating,
            "stock": spec.stock,
            "popularity": spec.popularity,
            "category": spec.category,
            "target_gender": spec.target_gender,
            "is_active": spec.is_active,
            "colors": spec.color_tuples(),
            "image_url": assets.catalog_url(spec.external_catalog_id),
            "description": spec.description,
        }

    # -- run ---------------------------------------------------------------------- #
    def run(self, on_progress: Optional[Callable[[int, int], None]] = None) -> Tuple[RunStats, dict]:
        cfg = self.cfg
        stats = RunStats(requested=cfg.count)
        products: List[dict] = []
        anchors: dict = {}
        vton: dict = {}
        manifest_entries: List[dict] = []

        for i in range(1, cfg.count + 1):
            spec = generate_spec(i, cfg, self.palette, self.registry)
            cat, subj, qa, passed = self._render_and_qa(spec)
            url = assets.catalog_url(spec.external_catalog_id)

            entry = {
                "external_catalog_id": spec.external_catalog_id,
                "template": spec.template.image_url,
                "category": spec.category,
                "target_gender": spec.target_gender,
                "colors": [
                    {"name": c.name, "hex": c.hex, "role": r, "percentage": p}
                    for c, r, p in zip(spec.colors, spec.roles, spec.percentages)
                ],
                "image_url": url,
                "cutout_url": "/tryon" + url,
                "garment_url": (
                    f"/api/v1/vton/garments/{spec.external_catalog_id}.png"
                    if assets.supports_vton_garment(spec) else None
                ),
                "vton_tier": spec.template.tier,
                "qa": qa.to_jsonable() if qa is not None else {"passed": True, "skipped": True},
                "persisted": passed,
            }
            manifest_entries.append(entry)

            if not passed:
                stats.failed += 1
                stats.failures.append({
                    "external_catalog_id": spec.external_catalog_id,
                    "reason": qa.reason if qa else "unknown",
                })
            else:
                if not cfg.dry_run:
                    self._persist_images(spec, cat, subj)
                products.append(self._seed_record(spec))
                a_url, anchor = assets.visual_anchor_entry(spec)
                v_url, vspec = assets.vton_seed_entry(spec, cfg)
                anchors[a_url] = anchor
                vton[v_url] = vspec
                stats.persisted += 1

            if on_progress and (i % 25 == 0 or i == cfg.count):
                on_progress(i, cfg.count)

        manifest = {
            "config": cfg.to_jsonable(),
            "summary": {
                "requested": stats.requested,
                "persisted": stats.persisted,
                "failed": stats.failed,
            },
            "failures": stats.failures,
            "entries": manifest_entries,
        }

        if not cfg.dry_run:
            emit.write_seed_module(
                cfg.out_seed, products, anchors, vton,
                count=cfg.count, seed=cfg.seed,
            )
            emit.write_manifest(cfg.out_manifest, manifest)

        return stats, manifest
