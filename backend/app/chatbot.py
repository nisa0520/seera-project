import re
from pathlib import Path

from .fuzzy import infer_layer1

try:
    import aiml
except ImportError:
    aiml = None


SKIN_TONE_HELP = "Pilih skin tone 1-6: 1=Very Fair, 2=Fair, 3=Medium Fair, 4=Moderate Brown, 5=Brown, 6=Dark Brown."
UNDERTONE_HELP = "Pilih undertone: cool/neutral/warm (atau 0/1/2)."


EDU_RESPONSES = {
    "skin tone": "Skin tone adalah tingkat kecerahan kulit (very fair sampai dark brown).",
    "undertone": "Undertone adalah nuansa dasar kulit: cool, neutral, atau warm.",
    "seasonal": "Seasonal color type dibagi 4: Spring, Summer, Autumn, Winter.",
    "spring": "Spring cocok dengan warna warm dan light.",
    "summer": "Summer cocok dengan warna cool dan light.",
    "autumn": "Autumn cocok dengan warna warm dan dark/medium.",
    "winter": "Winter cocok dengan warna cool dan dark/medium.",
}

_AIML_KERNEL = None


def init_aiml_kernel() -> None:
    global _AIML_KERNEL
    if _AIML_KERNEL is not None or aiml is None:
        return

    kernel = aiml.Kernel()
    aiml_file = Path(__file__).resolve().parent / "aiml" / "seera.aiml"
    if aiml_file.exists():
        kernel.learn(str(aiml_file))
    _AIML_KERNEL = kernel


def aiml_response(message: str) -> str | None:
    if _AIML_KERNEL is None:
        return None
    response = _AIML_KERNEL.respond(message.upper().strip())
    return response.strip() if response else None


def detect_education(message: str) -> str | None:
    msg = message.lower()
    for key, value in EDU_RESPONSES.items():
        if key in msg:
            return value
    return None


def parse_skin_tone(message: str) -> float | None:
    msg = message.lower()
    keyword_map = {
        "very fair": 1.0,
        "sangat cerah": 1.0,
        "fair": 2.0,
        "medium fair": 3.0,
        "moderate brown": 4.0,
        "brown": 5.0,
        "dark brown": 6.0,
        "gelap": 6.0,
    }
    for key, value in keyword_map.items():
        if key in msg:
            return value

    found = re.findall(r"\b([1-6])\b", message)
    if found:
        return float(found[0])
    return None


def parse_undertone(message: str) -> float | None:
    msg = message.lower()
    if "cool" in msg or "dingin" in msg:
        return 0.0
    if "neutral" in msg:
        return 1.0
    if "warm" in msg or "hangat" in msg:
        return 2.0

    found = re.findall(r"\b([0-2])\b", message)
    if found:
        return float(found[0])
    return None


def build_chat_response(message: str, skin_tone: float | None, undertone: float | None) -> tuple[str, float | None, float | None, str | None, float | None]:
    kernel_answer = aiml_response(message)
    if kernel_answer:
        return kernel_answer, skin_tone, undertone, None, None

    edu = detect_education(message)
    if edu:
        return edu, skin_tone, undertone, None, None

    parsed_skin = skin_tone if skin_tone is not None else parse_skin_tone(message)
    
    # Only parse undertone if skin_tone is already set, or if the user explicitly mentioned undertone keywords.
    # Otherwise a single digit like "1" might match both skin_tone and undertone.
    parsed_under = undertone
    if parsed_under is None:
        if skin_tone is not None:
            # We are in the "waiting for undertone" state
            parsed_under = parse_undertone(message)
        else:
            # We are in the "waiting for skin tone" state, but user might have typed both keywords
            msg_lower = message.lower()
            if "cool" in msg_lower or "neutral" in msg_lower or "warm" in msg_lower:
                parsed_under = parse_undertone(message)

    if parsed_skin is None:
        return f"Halo! Saya Seera Assistant. {SKIN_TONE_HELP}", None, None, None, None

    if parsed_under is None:
        return f"Skin tone tersimpan: {parsed_skin}. Sekarang {UNDERTONE_HELP}", parsed_skin, None, None, None

    result = infer_layer1(parsed_skin, parsed_under)
    bot_message = (
        f"Profiling selesai. Seasonal type kamu: {result.seasonal_type.title()} "
        f"(Y1={result.y1}). Lanjutkan rekomendasi dengan tombol 'Lihat Rekomendasi'."
    )
    return bot_message, parsed_skin, parsed_under, result.seasonal_type, result.y1


def parse_multimodal_blocks(text: str) -> list[dict]:
    """Parse text containing <visual>, <palette>, <product-card>, <chart> tags into JSON blocks."""
    blocks = []
    
    # regex to match any of the custom tags
    pattern = r'(<visual[^>]*>|<palette[^>]*>|<product-card[^>]*>|<chart[^>]*>)'
    
    parts = re.split(pattern, text)
    
    visuals_db = {
        "fitzpatrick_scale": {"type": "infographic", "url": "/about.png", "alt": "Skala Fitzpatrick (Testing Local Image)"},
        "undertone_comparison": {"type": "infographic", "url": "https://placehold.co/600x300/f5f5f5/333333?text=Perbandingan+Undertone", "alt": "Warm vs Cool vs Neutral"},
        "palette_spring": {"type": "palette", "url": "https://placehold.co/400x200/F4C2C2/333?text=Palet+Spring", "alt": "Palet Spring"},
        "palette_summer": {"type": "palette", "url": "https://placehold.co/400x200/B0C4DE/333?text=Palet+Summer", "alt": "Palet Summer"},
        "palette_autumn": {"type": "palette", "url": "https://placehold.co/400x200/D2B48C/333?text=Palet+Autumn", "alt": "Palet Autumn"},
        "palette_winter": {"type": "palette", "url": "https://placehold.co/400x200/E6E6FA/333?text=Palet+Winter", "alt": "Palet Winter"},
        "seasonal_overview": {"type": "infographic", "url": "https://placehold.co/600x400/f5f5f5/333?text=4+Musim+Warna", "alt": "4 Musim Warna"},
        "mascot_seera": {"type": "illustration", "url": "https://placehold.co/200x200/c9a86a/fff?text=Seera", "alt": "Maskot Seera"},
        "rgb_to_hsv_diagram": {"type": "infographic", "url": "https://placehold.co/500x300/f5f5f5/333?text=Tips+Fashion", "alt": "Tips Fashion Diagram"}
    }

    for part in parts:
        if not part.strip():
            continue
            
        if part.startswith('<visual'):
            match = re.search(r'ref="([^"]+)"', part)
            if match:
                ref = match.group(1)
                asset = visuals_db.get(ref)
                if asset:
                    blocks.append({"type": "image", "url": asset["url"], "alt": asset["alt"]})
                else:
                    blocks.append({"type": "image", "url": f"https://placehold.co/600x300/f5f5f5/333333?text={ref}", "alt": f"Visual {ref}"})
        elif part.startswith('<palette'):
            match = re.search(r'season="([^"]+)"', part)
            if match:
                season = match.group(1)
                asset = visuals_db.get(f"palette_{season}")
                if asset:
                    blocks.append({"type": "palette", "url": asset["url"], "alt": asset["alt"]})
                else:
                    blocks.append({"type": "palette", "url": f"https://placehold.co/400x200/cccccc/333?text=Palette+{season}", "alt": f"Palette {season}"})
        elif part.startswith('<product-card'):
            match = re.search(r'id="([^"]+)"', part)
            if match:
                pid = match.group(1)
                blocks.append({"type": "product-card", "data": {"id": pid}})
        elif part.startswith('<chart'):
            match_type = re.search(r'type="([^"]+)"', part)
            match_data = re.search(r'data="([^"]+)"', part)
            if match_type and match_data:
                blocks.append({"type": "chart", "chart_type": match_type.group(1), "data_ref": match_data.group(1)})
        else:
            # Clean up newlines for text
            clean_text = part.strip()
            if clean_text:
                blocks.append({"type": "text", "content": clean_text})
                
    if not blocks:
        blocks = [{"type": "text", "content": text}]
        
    return blocks
