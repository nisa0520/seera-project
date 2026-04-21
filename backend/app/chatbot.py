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
    parsed_under = undertone if undertone is not None else parse_undertone(message)

    if parsed_skin is None:
        return f"Halo! Saya Seera Assistant. {SKIN_TONE_HELP}", None, None, None, None

    if parsed_under is None:
        return f"Skin tone tersimpan: {parsed_skin}. Sekarang {UNDERTONE_HELP}", parsed_skin, None, None, None

    result = infer_layer1(parsed_skin, parsed_under)
    bot_message = (
        f"Profiling selesai. Seasonal type kamu: {result.seasonal_type.title()} "
        f"(Y1={result.y1}). Lanjutkan rekomendasi dengan tombol 'Generate Rekomendasi'."
    )
    return bot_message, parsed_skin, parsed_under, result.seasonal_type, result.y1
