"""Generator configuration (all tunables in one place, fully serialisable)."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Sequence

from app.catalog_gen import paths


# Default colour-count distribution P(k=1..4). The schema caps color_rank at 4
# and forbids duplicate roles, so k is bounded to 4 (DOMINANT/SECONDARY/ACCENT/MOTIF).
DEFAULT_COLOR_DISTRIBUTION = (0.50, 0.30, 0.15, 0.05)

# ID scheme distinct from hand-authored SK-xxx.
ID_PREFIX = "GEN-"
ID_WIDTH = 6


@dataclass
class GenConfig:
    """Immutable-ish run configuration. Same config + same id => identical output."""

    count: int = 1000
    seed: int = 42  # global run salt; mixed into every per-product seed
    color_distribution: Sequence[float] = DEFAULT_COLOR_DISTRIBUTION

    # Output locations.
    out_catalog_dir: Path = field(default_factory=lambda: paths.DEFAULT_CATALOG_DIR)
    out_cutout_dir: Path = field(default_factory=lambda: paths.DEFAULT_CUTOUT_DIR)
    out_garment_dir: Path = field(default_factory=lambda: paths.DEFAULT_GARMENT_DIR)
    out_manifest: Path = field(default_factory=lambda: paths.DEFAULT_MANIFEST)
    out_seed: Path = field(default_factory=lambda: paths.DEFAULT_SEED_OUT)

    # Template restriction (None = all). Values are garment types: koko/gamis/abaya/hijab.
    limit_templates: Optional[Sequence[str]] = None

    # QA gate.
    qa_enabled: bool = True
    qa_area_tolerance_pp: float = 10.0      # ± percentage-points on area share
    qa_delta_e_threshold: float = 12.0      # max ΔE2000 cluster<->metadata
    qa_retry_budget: int = 3                # deterministic re-render attempts
    qa_sample_cap: int = 4000               # max garment pixels fed to KMeans

    # Colour selection harmony.
    min_pairwise_delta_e: float = 14.0      # selected colours must be distinguishable
    min_color_share_pp: float = 10.0        # smallest rendered share (helps QA detect it)

    # Recolor.
    synthetic_quality_penalty: float = 0.05  # subtracted from inherited VTON score

    dry_run: bool = False

    def color_count_weights(self) -> list[float]:
        w = [max(0.0, float(x)) for x in self.color_distribution][:4]
        while len(w) < 4:
            w.append(0.0)
        total = sum(w)
        if total <= 0:
            return [1.0, 0.0, 0.0, 0.0]
        return [x / total for x in w]

    def to_jsonable(self) -> dict:
        d = asdict(self)
        for k, v in list(d.items()):
            if isinstance(v, Path):
                d[k] = str(v)
            elif isinstance(v, tuple):
                d[k] = list(v)
        return d
