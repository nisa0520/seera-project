"""Seed education topics and contents - internal knowledge base."""
from sqlalchemy.orm import Session as DBSession
from app.models.education import EducationTopic, EducationContent


EDUCATION_SEED = [
    {
        "code": "SKIN_TONE",
        "title": "Apa itu skin tone?",
        "description": "Klasifikasi warna kulit menurut Fitzpatrick.",
        "display_order": 1,
        "content": (
            "Skin tone adalah warna permukaan kulit yang umumnya diklasifikasikan menggunakan skala "
            "Fitzpatrick Tipe I hingga VI. Tipe I sangat terang (mudah terbakar matahari), sementara "
            "Tipe VI sangat gelap. Skin tone berbeda dengan undertone; skin tone bisa berubah karena "
            "paparan sinar matahari, sedangkan undertone bersifat permanen."
        ),
        "source_note": "Knowledge base internal berdasarkan PRD Seera Project.",
    },
    {
        "code": "UNDERTONE",
        "title": "Apa itu undertone?",
        "description": "Nuansa dasar di bawah permukaan kulit.",
        "display_order": 2,
        "content": (
            "Undertone adalah nuansa dasar warna kulit yang ada di bawah permukaan dan tidak berubah "
            "akibat sinar matahari. Ada tiga kategori utama: Cool (kebiruan/keunguan), Warm "
            "(kekuningan/keemasan), dan Neutral (campuran). Salah satu cara mengeceknya adalah dengan "
            "melihat warna urat di pergelangan tangan: biru/ungu cenderung Cool, hijau cenderung Warm, "
            "campuran berarti Neutral."
        ),
        "source_note": "Knowledge base internal berdasarkan PRD Seera Project.",
    },
    {
        "code": "SEASONAL_COLOR_TYPE",
        "title": "Apa itu seasonal color type?",
        "description": "Empat musim warna personal: Spring, Summer, Autumn, Winter.",
        "display_order": 3,
        "content": (
            "Seasonal Color Type adalah klasifikasi profil warna pribadi yang membagi orang ke dalam "
            "empat musim:\n"
            "• Spring: warm, light, bright - cocok dengan warna cerah, segar, warm.\n"
            "• Summer: cool, light, soft - cocok dengan warna lembut, sejuk, pastel.\n"
            "• Autumn: warm, deep, earthy - cocok dengan warna bumi yang hangat dan dalam.\n"
            "• Winter: cool, deep, clear - cocok dengan warna kontras, tegas, dan sejuk.\n"
            "Sistem Seera menentukan musim Anda menggunakan kombinasi skin tone dan undertone melalui "
            "Fuzzy Inference System Layer 1."
        ),
        "source_note": "Knowledge base internal berdasarkan PRD Seera Project.",
    },
]


def seed_education(db: DBSession) -> None:
    for entry in EDUCATION_SEED:
        topic = (
            db.query(EducationTopic).filter(EducationTopic.code == entry["code"]).first()
        )
        if not topic:
            topic = EducationTopic(
                code=entry["code"],
                title=entry["title"],
                description=entry["description"],
                display_order=entry["display_order"],
                is_active=True,
            )
            db.add(topic)
            db.flush()
        else:
            topic.title = entry["title"]
            topic.description = entry["description"]
            topic.display_order = entry["display_order"]
            topic.is_active = True

        content = (
            db.query(EducationContent)
            .filter(EducationContent.topic_id == topic.id)
            .order_by(EducationContent.version.desc())
            .first()
        )
        if not content:
            db.add(
                EducationContent(
                    topic_id=topic.id,
                    content=entry["content"],
                    source_note=entry["source_note"],
                    version=1,
                    is_active=True,
                )
            )
        else:
            content.content = entry["content"]
            content.source_note = entry["source_note"]
            content.is_active = True
    db.commit()
