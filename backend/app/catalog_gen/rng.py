"""Deterministic seeding utilities.

The per-product seed is a **stable** hash of ``external_catalog_id`` mixed with an
optional global run salt. We use ``hashlib.blake2b`` rather than the builtin
``hash()`` because the latter is randomised per interpreter run (``PYTHONHASHSEED``)
and would break the "same inputs => byte-identical output" guarantee.

Each stage (template choice, k, colours, percentages, scalars, partition, QA retry)
draws from a *namespaced* sub-stream so that all randomness is reproducible and
independent across stages.
"""
from __future__ import annotations

import hashlib
import random

import numpy as np


def stable_seed(external_catalog_id: str, salt: int = 0, stream: str = "") -> int:
    """Return a stable 32-bit seed for an id (+ optional salt + stream namespace)."""
    key = f"{salt}|{stream}|{external_catalog_id}".encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=8).digest()
    return int.from_bytes(digest, "big") & 0x7FFFFFFF


class Deterministic:
    """Bundle of reproducible RNGs for a single product, namespaced per stage."""

    def __init__(self, external_catalog_id: str, salt: int = 0):
        self.external_catalog_id = external_catalog_id
        self.salt = salt

    def seed(self, stream: str) -> int:
        return stable_seed(self.external_catalog_id, self.salt, stream)

    def numpy(self, stream: str) -> np.random.RandomState:
        return np.random.RandomState(self.seed(stream))

    def python(self, stream: str) -> random.Random:
        return random.Random(self.seed(stream))
