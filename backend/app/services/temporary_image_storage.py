"""TemporaryImageStorage: penyimpanan file image sementara ber-expiry (BR-VTO-08).

Foto pengguna, mask, dan hasil try-on hanya hidup selama sesi/TTL — file diberi
token acak dan dihapus otomatis saat kedaluwarsa (NFR-VTO-02/03).
"""
import secrets
import time
from pathlib import Path
from typing import Optional

from app.core.config import settings


def _root() -> Path:
    root = Path(settings.VTON_TEMP_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _path_for(token: str) -> Path:
    # Token dibuat oleh save(); cegah path traversal dari token eksternal.
    safe = "".join(c for c in token if c.isalnum() or c in "._-")
    return _root() / safe


def save(content: bytes, suffix: str = ".png") -> str:
    """Simpan bytes; kembalikan token acak yang tidak dapat ditebak."""
    cleanup_expired()
    token = secrets.token_urlsafe(24) + suffix
    _path_for(token).write_bytes(content)
    return token


def load(token: str) -> Optional[bytes]:
    path = _path_for(token)
    if not path.is_file():
        return None
    if _is_expired(path):
        path.unlink(missing_ok=True)
        return None
    return path.read_bytes()


def path(token: str) -> Optional[str]:
    p = _path_for(token)
    if not p.is_file() or _is_expired(p):
        return None
    return str(p)


def delete(token: str) -> None:
    _path_for(token).unlink(missing_ok=True)


def _is_expired(p: Path) -> bool:
    ttl = settings.VTON_IMAGE_TTL_MINUTES * 60
    return (time.time() - p.stat().st_mtime) > ttl


def cleanup_expired() -> None:
    try:
        for p in _root().iterdir():
            if p.is_file() and _is_expired(p):
                p.unlink(missing_ok=True)
    except OSError:
        pass
