"""Seed AIML categories - all chatbot templates in Bahasa Indonesia."""
from sqlalchemy.orm import Session as DBSession
from app.models.aiml_category import AIMLCategory


GENDER_QR = [
    {"label": "Pria", "value": "MALE"},
    {"label": "Wanita", "value": "FEMALE"},
    {"label": "Semua koleksi", "value": "PREFER_NOT_TO_SAY"},
]

SKINTONE_QR = [
    {"label": "Tipe I - Very Fair", "value": "I"},
    {"label": "Tipe II - Fair", "value": "II"},
    {"label": "Tipe III - Medium Fair", "value": "III"},
    {"label": "Tipe IV - Moderate Brown", "value": "IV"},
    {"label": "Tipe V - Brown", "value": "V"},
    {"label": "Tipe VI - Dark Brown", "value": "VI"},
]

UNDERTONE_QR = [
    {"label": "Cool", "value": "COOL"},
    {"label": "Neutral", "value": "NEUTRAL"},
    {"label": "Warm", "value": "WARM"},
]

CONFIRM_QR = [
    {"label": "Ya, proses rekomendasi", "value": "CONFIRM", "primary": True},
    {"label": "Ubah preferensi koleksi", "value": "CHANGE_GENDER"},
    {"label": "Ubah skin tone", "value": "CHANGE_SKIN_TONE"},
    {"label": "Ubah undertone", "value": "CHANGE_UNDERTONE"},
]

CHANGE_QR = [
    {"label": "Ubah preferensi koleksi", "value": "CHANGE_GENDER"},
    {"label": "Ubah skin tone", "value": "CHANGE_SKIN_TONE"},
    {"label": "Ubah undertone", "value": "CHANGE_UNDERTONE"},
]

POST_RECOMMENDATION_QR = [
    {"label": "Urutkan harga termurah", "value": "FILTER_PRICE_ASC"},
    {"label": "Urutkan rating tertinggi", "value": "FILTER_RATING_DESC"},
    {"label": "Urutkan popularitas", "value": "FILTER_POPULARITY_DESC"},
    {"label": "Warna yang dihindari", "value": "COLORS_TO_AVOID"},
    {"label": "Beri umpan balik", "value": "FEEDBACK"},
]

EDU_TOPICS_QR = [
    {"label": "Apa Itu Skin Tone?", "value": "SKIN_TONE"},
    {"label": "Apa Itu Undertone?", "value": "UNDERTONE"},
    {"label": "Apa Itu Seasonal Color Theory?", "value": "SEASONAL_COLOR_TYPE"},
    {"label": "Cara Menentukan Skin Tone", "value": "DETERMINE_SKIN_TONE"},
    {"label": "Cara Menentukan Undertone", "value": "DETERMINE_UNDERTONE"},
    {"label": "Mulai rekomendasi", "value": "START_RECOMMENDATION"},
]


AIML_SEED = [
    {
        "pattern": "WELCOME_AND_GENDER_LIST",
        "template": (
            "Halo! Saya akan bantu rekomendasikan warna pakaian yang sesuai dengan kulit Anda. "
            "Supaya pilihan produknya terasa lebih relevan, boleh pilih koleksi yang paling nyaman "
            "untuk Anda lihat. Ini hanya dipakai untuk menyesuaikan rekomendasi."
        ),
        "quick_replies": GENDER_QR,
    },
    {
        "pattern": "INVALID_GENDER",
        "template": "Pilihan koleksi belum sesuai. Silakan pilih Pria, Wanita, atau Semua koleksi.",
        "quick_replies": GENDER_QR,
    },
    {
        "pattern": "WELCOME_AND_SKINTONE_LIST",
        "template": (
            "Terima kasih. Sekarang pilih skin tone Anda berdasarkan skala Fitzpatrick Tipe I sampai VI."
        ),
        "quick_replies": SKINTONE_QR,
    },
    {
        "pattern": "UNDERTONE_LIST",
        "template": (
            "Terima kasih. Skin tone Anda: {skin_tone_name}. "
            "Sekarang pilih undertone Anda: Cool, Neutral, atau Warm."
        ),
        "quick_replies": UNDERTONE_QR,
    },
    {
        "pattern": "INVALID_SKINTONE",
        "template": "Pilihan skin tone tidak sesuai. Silakan pilih Tipe I sampai VI.",
        "quick_replies": SKINTONE_QR,
    },
    {
        "pattern": "INVALID_UNDERTONE",
        "template": "Pilihan undertone tidak sesuai. Silakan pilih Cool, Neutral, atau Warm.",
        "quick_replies": UNDERTONE_QR,
    },
    {
        "pattern": "SUMMARY_AND_CONFIRMATION",
        "template": (
            "Ringkasan pilihan Anda: preferensi koleksi {gender_name}, "
            "skin tone {skin_tone_name}, undertone {undertone_name}. "
            "Apakah sudah sesuai?"
        ),
        "quick_replies": CONFIRM_QR,
    },
    {
        "pattern": "CHANGE_SELECTION_OPTIONS",
        "template": "Bagian mana yang ingin Anda ubah? Preferensi koleksi, skin tone, atau undertone?",
        "quick_replies": CHANGE_QR,
    },
    {
        "pattern": "PRODUCT_RECOMMENDATIONS",
        "template": (
            "Berikut {top_n} rekomendasi produk yang paling cocok untuk Anda berdasarkan profil "
            "{seasonal_name} dan preferensi koleksi {gender_name}."
        ),
        "quick_replies": POST_RECOMMENDATION_QR,
    },
    {
        "pattern": "FILTERED_RECOMMENDATIONS",
        "template": "Berikut rekomendasi yang sudah diurutkan ulang sesuai kriteria pilihan Anda.",
        "quick_replies": POST_RECOMMENDATION_QR,
    },
    {
        "pattern": "COLORS_TO_AVOID",
        "template": "Berikut warna yang sebaiknya dihindari berdasarkan profil personal color Anda.",
        "quick_replies": POST_RECOMMENDATION_QR,
    },
    {
        "pattern": "NOT_UNDERSTOOD",
        "template": (
            "Maaf, saya belum memahami permintaan Anda. Silakan pilih salah satu opsi yang tersedia "
            "atau mulai dari preferensi koleksi."
        ),
        "quick_replies": [
            {"label": "Mulai profiling", "value": "START_PROFILING", "primary": True},
            {"label": "Belajar personal color", "value": "EDUCATION"},
        ],
    },
    {
        "pattern": "TOPIC_UNAVAILABLE",
        "template": "Topik '{topic_code}' belum tersedia. Silakan pilih topik lain.",
        "quick_replies": EDU_TOPICS_QR,
    },
    {
        "pattern": "EDUCATION_TOPICS_LIST",
        "template": "Pilih topik personal color yang ingin Anda pelajari.",
        "quick_replies": EDU_TOPICS_QR,
    },
    {
        "pattern": "FEEDBACK_THANKS",
        "template": "Terima kasih atas umpan balik Anda!",
        "quick_replies": None,
    },
]


def seed_aiml(db: DBSession) -> None:
    for entry in AIML_SEED:
        existing = (
            db.query(AIMLCategory)
            .filter(AIMLCategory.pattern == entry["pattern"])
            .first()
        )
        if existing:
            existing.template = entry["template"]
            existing.quick_replies = entry.get("quick_replies")
            existing.is_active = True
        else:
            db.add(
                AIMLCategory(
                    pattern=entry["pattern"],
                    template=entry["template"],
                    quick_replies=entry.get("quick_replies"),
                    is_active=True,
                )
            )
    db.commit()
