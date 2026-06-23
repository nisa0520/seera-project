"""Garment caption builder untuk IDM-VTON (PRD AssetTier 15.5 no. 5, FR-VTO-09).

IDM-VTON memakai deskripsi tekstual garment (`garment_des`) untuk memperkuat
garment fidelity. Caption dibangun deterministik & detail dari metadata produk:
kategori, warna dominan, panjang lengan, jenis kerah/leher, pola/motif, dan
material/tekstur bila tersedia. Konsisten dan dapat ditelusuri pada
`vton_jobs.garment_caption` (BR-VTO-13/15).

Contoh: "a navy long-sleeve button-up koko shirt with a mandarin collar and a
waffle texture".
"""
from typing import Optional

from app.models.product import Product


# Frasa dasar garment: (base_noun, sleeve, collar) dalam bahasa Inggris
# (IDM-VTON dilatih dengan caption bahasa Inggris).
_GARMENT_SPECS = [
    ("koko", {"noun": "koko muslim shirt", "sleeve": "long-sleeve", "collar": "a mandarin collar", "gender": "men's"}),
    ("gamis", {"noun": "flowing gamis dress", "sleeve": "long-sleeve", "collar": "a round neckline", "gender": "women's"}),
    ("abaya", {"noun": "abaya robe", "sleeve": "long-sleeve", "collar": "a round neckline", "gender": "women's"}),
    ("khimar", {"noun": "khimar veil", "sleeve": None, "collar": None, "gender": "women's"}),
    ("hijab", {"noun": "hijab head covering", "sleeve": None, "collar": None, "gender": None}),
    ("dress", {"noun": "dress", "sleeve": "long-sleeve", "collar": "a round neckline", "gender": "women's"}),
    ("outer", {"noun": "outer jacket", "sleeve": "long-sleeve", "collar": "a collar", "gender": None}),
]

_CATEGORY_SPECS = {
    "atasan": {"noun": "top", "sleeve": "long-sleeve", "collar": None, "gender": None},
    "dress": {"noun": "dress", "sleeve": "long-sleeve", "collar": "a round neckline", "gender": "women's"},
    "outer": {"noun": "outer garment", "sleeve": "long-sleeve", "collar": "a collar", "gender": None},
    "aksesoris": {"noun": "accessory", "sleeve": None, "collar": None, "gender": None},
}

# Deteksi pola/motif & material dari nama produk.
_PATTERN_KEYWORDS = {
    "batik": "a batik pattern",
    "floral": "a floral pattern",
    "bunga": "a floral pattern",
    "stripe": "a striped pattern",
    "garis": "a striped pattern",
    "polkadot": "a polka-dot pattern",
    "motif": "a patterned design",
}
_MATERIAL_KEYWORDS = {
    "waffle": "a waffle texture",
    "linen": "a linen texture",
    "katun": "a cotton texture",
    "cotton": "a cotton texture",
    "satin": "a satin finish",
    "denim": "a denim texture",
}
_DETAIL_KEYWORDS = {
    "bordir": "embroidery detail",
    "embroider": "embroidery detail",
    "logo": "a small logo",
    "kancing": "button-up front",
    "button": "button-up front",
}


def _spec_for(product: Product) -> dict:
    name = (product.name or "").lower()
    for keyword, spec in _GARMENT_SPECS:
        if keyword in name:
            return spec
    category = (product.category.name.lower() if product.category and product.category.name else "")
    return _CATEGORY_SPECS.get(category, {"noun": "clothing item", "sleeve": "long-sleeve", "collar": None, "gender": None})


def _dominant_color_name(product: Product) -> Optional[str]:
    colors_sorted = sorted(product.product_colors, key=lambda pc: pc.color_rank)
    for pc in colors_sorted:
        if pc.color_role == "DOMINANT" and pc.color:
            return pc.color.color_name
    if colors_sorted and colors_sorted[0].color:
        return colors_sorted[0].color.color_name
    return None


def _keyword_match(name: str, mapping: dict) -> Optional[str]:
    for keyword, phrase in mapping.items():
        if keyword in name:
            return phrase
    return None


def build_garment_caption(product: Product) -> str:
    """Caption garment detail dari metadata produk untuk IDM-VTON (garment_des)."""
    name = (product.name or "").lower()
    spec = _spec_for(product)
    color = _dominant_color_name(product)

    # Susun frasa inti: <article> <color> <sleeve> <pattern?> <button?> <noun>
    parts = []
    pattern = _keyword_match(name, _PATTERN_KEYWORDS)
    material = _keyword_match(name, _MATERIAL_KEYWORDS)
    detail = _keyword_match(name, _DETAIL_KEYWORDS)

    head_words = []
    if color:
        head_words.append(color.lower())
    if spec.get("sleeve"):
        head_words.append(spec["sleeve"])
    if detail == "button-up front":
        head_words.append("button-up")
    if spec.get("gender"):
        head_words.append(spec["gender"])
    head_words.append(spec["noun"])

    core = " ".join(head_words)
    article = "an" if core[:1] in "aeiou" else "a"
    caption = f"{article} {core}"

    # Tambahan detail: kerah, pola, material, embroidery/logo.
    trailers = []
    if spec.get("collar"):
        trailers.append(spec["collar"])
    if pattern:
        trailers.append(pattern)
    if material:
        trailers.append(material)
    if detail in ("embroidery detail", "a small logo"):
        trailers.append(detail)

    if trailers:
        caption += " with " + ", ".join(trailers)
    return caption.strip()
