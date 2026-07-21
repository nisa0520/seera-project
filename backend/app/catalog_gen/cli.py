"""CLI for the synthetic catalog generator.

Examples::

    python -m app.catalog_gen --count 1000 --seed 42
    python -m app.catalog_gen --count 50 --limit-templates koko,gamis --dry-run
    python -m app.catalog_gen --author-masks-only          # (re)build cached masks

Defaults write:
  * catalog PNGs -> public/generated/
  * try-on cutouts -> public/tryon/generated/
  * manifest -> build/generated_manifest.json
  * seed module -> backend/app/seed/generated/generated_products.py  (importable)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional, Sequence

from app.catalog_gen import paths
from app.catalog_gen.config import GenConfig, DEFAULT_COLOR_DISTRIBUTION


def _resolve(p: Optional[str], default: Path) -> Path:
    if not p:
        return default
    path = Path(p)
    return path if path.is_absolute() else (paths.REPO_ROOT / path)


def _parse_distribution(s: Optional[str]) -> Sequence[float]:
    if not s:
        return DEFAULT_COLOR_DISTRIBUTION
    parts = [float(x) for x in s.split(",") if x.strip() != ""]
    if not parts:
        raise argparse.ArgumentTypeError("empty --color-distribution")
    return tuple(parts)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate-catalog",
        description="Generate synthetic catalog data + reference-based images (additive).",
    )
    p.add_argument("--count", type=int, default=1000, help="number of products (default 1000)")
    p.add_argument("--seed", type=int, default=42, help="global run salt (default 42)")
    p.add_argument("--color-distribution", type=str, default=None,
                   help="P(k=1..4), e.g. 0.5,0.3,0.15,0.05")
    p.add_argument("--out-images", type=str, default=None,
                   help="catalog image dir (default public/generated)")
    p.add_argument("--out-cutouts", type=str, default=None,
                   help="try-on cutout dir (default public/tryon/generated)")
    p.add_argument("--out-manifest", type=str, default=None,
                   help="manifest JSON path (default build/generated_manifest.json)")
    p.add_argument("--emit-seed", type=str, default=None,
                   help="PRODUCTS_SEED-compatible module path "
                        "(default backend/app/seed/generated/generated_products.py)")
    p.add_argument("--limit-templates", type=str, default=None,
                   help="comma list of garment types: koko,gamis,abaya,hijab")
    p.add_argument("--dry-run", action="store_true", help="render+QA but write nothing")
    p.add_argument("--no-qa", action="store_true", help="skip the ΔE2000 QA gate")
    p.add_argument("--qa-tolerance", type=float, default=10.0, help="area tolerance (pp)")
    p.add_argument("--qa-delta-e", type=float, default=12.0, help="max ΔE2000 per colour")
    p.add_argument("--retry-budget", type=int, default=3, help="deterministic re-render attempts")
    p.add_argument("--author-masks", action="store_true",
                   help="(re)build cached template masks before generating")
    p.add_argument("--author-masks-only", action="store_true",
                   help="only (re)build cached template masks, then exit")
    p.add_argument("--quiet", action="store_true", help="suppress progress output")
    return p


def config_from_args(args: argparse.Namespace) -> GenConfig:
    limit = None
    if args.limit_templates:
        limit = [x.strip() for x in args.limit_templates.split(",") if x.strip()]
    return GenConfig(
        count=args.count,
        seed=args.seed,
        color_distribution=_parse_distribution(args.color_distribution),
        out_catalog_dir=_resolve(args.out_images, paths.DEFAULT_CATALOG_DIR),
        out_cutout_dir=_resolve(args.out_cutouts, paths.DEFAULT_CUTOUT_DIR),
        out_manifest=_resolve(args.out_manifest, paths.DEFAULT_MANIFEST),
        out_seed=_resolve(args.emit_seed, paths.DEFAULT_SEED_OUT),
        limit_templates=limit,
        qa_enabled=not args.no_qa,
        qa_area_tolerance_pp=args.qa_tolerance,
        qa_delta_e_threshold=args.qa_delta_e,
        qa_retry_budget=args.retry_budget,
        dry_run=args.dry_run,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    # Import here so --help works without pulling heavy deps.
    from app.catalog_gen.pipeline import Generator
    from app.catalog_gen.masks import author_all

    cfg = config_from_args(args)

    if args.author_masks or args.author_masks_only:
        from app.catalog_gen.templates import TemplateRegistry
        n = author_all(TemplateRegistry(cfg.limit_templates).templates, force=True)
        print(f"Authored/cached masks for {n} templates -> {paths.MASK_CACHE_DIR}")
        if args.author_masks_only:
            return 0

    started = time.time()

    def on_progress(i: int, total: int) -> None:
        if not args.quiet:
            pct = i / total * 100
            print(f"\r  {i}/{total} ({pct:5.1f}%)", end="", flush=True)

    gen = Generator(cfg)
    stats, _ = gen.run(on_progress=on_progress)
    if not args.quiet:
        print()

    elapsed = time.time() - started
    print(
        f"Done in {elapsed:.1f}s — requested={stats.requested} "
        f"persisted={stats.persisted} failed_qa={stats.failed}"
    )
    if not cfg.dry_run:
        print(f"  manifest : {cfg.out_manifest}")
        print(f"  seed mod : {cfg.out_seed}")
        print(f"  images   : {cfg.out_catalog_dir}")
        print("Run the seeder to ingest: python -m app.seed.run_seed")
    if stats.failed:
        print(f"  note: {stats.failed} entries failed QA and were NOT persisted "
              f"(see manifest.failures).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
