"""Preprocessing offline: hapus background foto produk untuk virtual try-on.

Menghasilkan PNG transparan di public/tryon/ dengan ukuran kanvas SAMA dengan
foto asli, sehingga anotasi face anchor (fraksi dimensi foto) tetap berlaku.

Jalankan sekali dari folder backend (rembg hanya diperlukan saat preprocessing,
bukan dependency runtime):

    .venv/bin/python scripts/generate_tryon_cutouts.py
"""
import io
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC = PROJECT_ROOT / "public"
OUT = PUBLIC / "tryon"

FILES = [
    "koko-putih.png", "koko-abu.png", "koko-biru.png", "koko-hijau.png",
    "koko-coklat.png", "koko-bt.png", "koko-t.png", "koko-w.png", "koko.png",
    "abaya-hitam.png", "gamis-pink.png", "gamis-coklat.png", "gamis-p.png",
    "gamis.png", "abaya.png", "hijab.png",
]

DEFAULT_MODEL = "isnet-general-use"
# Subjek senada dengan background membuat isnet gagal; human-seg lebih andal di sini.
MODEL_OVERRIDES = {
    "hijab.png": "u2net_human_seg",
    "koko.png": "u2net_human_seg",
}

# Sisa kepala model pada foto (mode try-on ABOVE) dihapus agar tidak mengintip
# di belakang kepala pengguna. Elips dalam fraksi dimensi foto, tepi di-feather.
HEAD_ERASE = {
    "koko-abu.png":    {"cx": 0.56, "cy": 0.03, "rx": 0.12, "ry": 0.060},
    "koko-biru.png":   {"cx": 0.42, "cy": 0.00, "rx": 0.12, "ry": 0.045},
    "koko-coklat.png": {"cx": 0.45, "cy": 0.00, "rx": 0.09, "ry": 0.050},
    "koko-w.png":      {"cx": 0.56, "cy": 0.01, "rx": 0.10, "ry": 0.070},
    "koko-t.png":      {"cx": 0.50, "cy": 0.08, "rx": 0.11, "ry": 0.105},
}


def _erase_model_head(cutout: Image.Image, erase: dict) -> Image.Image:
    import numpy as np
    import cv2

    rgba = np.array(cutout)
    h, w = rgba.shape[:2]
    hole = np.zeros((h, w), dtype="uint8")
    cv2.ellipse(
        hole,
        (int(erase["cx"] * w), int(erase["cy"] * h)),
        (int(erase["rx"] * w), int(erase["ry"] * h)),
        0, 0, 360, 255, -1,
    )
    hole = cv2.GaussianBlur(hole, (15, 15), 0)
    alpha = rgba[:, :, 3].astype("int16") - hole.astype("int16")
    rgba[:, :, 3] = alpha.clip(0, 255).astype("uint8")
    return Image.fromarray(rgba, mode="RGBA")


def main() -> int:
    OUT.mkdir(exist_ok=True)
    sessions = {}
    for name in FILES:
        src = PUBLIC / name
        if not src.exists():
            print(f"LEWAT  {name} (tidak ditemukan)")
            continue
        model = MODEL_OVERRIDES.get(name, DEFAULT_MODEL)
        if model not in sessions:
            sessions[model] = new_session(model)
        original = Image.open(src).convert("RGB")
        cutout = remove(
            original,
            session=sessions[model],
            post_process_mask=True,
        ).convert("RGBA")
        if cutout.size != original.size:
            cutout = cutout.resize(original.size)
        if name in HEAD_ERASE:
            cutout = _erase_model_head(cutout, HEAD_ERASE[name])
        cutout.save(OUT / name)
        print(f"OK     {name} ({model}) -> public/tryon/{name} {cutout.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
