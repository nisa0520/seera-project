"""Seed education topics and contents - internal knowledge base."""
from sqlalchemy.orm import Session as DBSession
from app.models.education import EducationTopic, EducationContent


EDUCATION_SEED = [
    {
        "code": "SKIN_TONE",
        "title": "Apa Itu Skin Tone?",
        "description": "Warna kulit yang terlihat dari luar dan dipengaruhi oleh melanin.",
        "display_order": 1,
        "content": (
            "Skin tone adalah warna kulit yang terlihat dari luar, yaitu warna yang langsung bisa "
            "kamu lihat dengan mata. Warna ini ditentukan terutama oleh melanin, pigmen alami yang "
            "diproduksi kulit. Makin banyak melanin, makin gelap warna kulitnya.\n\n"
            "Skin tone bisa berubah, misalnya menjadi lebih gelap karena sering terkena matahari. "
            "Untuk kulit orang Indonesia, skin tone umumnya terbagi menjadi tiga:\n"
            "• Putih: kulit cerah, cenderung kemerahan atau pink.\n"
            "• Kuning langsat: kulit terang kekuningan atau gading, dan sangat umum di Indonesia.\n"
            "• Sawo matang: kulit cokelat medium, biasanya terasa hangat atau netral."
        ),
        "source_note": "Knowledge base internal: knowledge_base_warna_kulit (1).pdf.",
    },
    {
        "code": "UNDERTONE",
        "title": "Apa Itu Undertone?",
        "description": "Rona warna dasar kulit yang tersembunyi di bawah permukaan.",
        "display_order": 2,
        "content": (
            "Undertone adalah rona warna dasar kulit yang tersembunyi di bawah permukaan. Berbeda "
            "dari skin tone yang bisa berubah, undertone sifatnya permanen dan tidak berubah sepanjang "
            "hidupmu. Dua orang bisa punya skin tone yang sama tapi undertone berbeda, dan ini yang "
            "lebih menentukan dalam pemilihan warna pakaian yang cocok.\n\n"
            "Ada tiga jenis undertone:\n"
            "• Warm: rona dasarnya kuning, keemasan, atau peach. Kulit tampak bercahaya keemasan. "
            "Mayoritas orang Indonesia dengan kulit kuning langsat dan sawo matang masuk kategori ini.\n"
            "• Cool: rona dasarnya merah muda atau kebiruan. Kulit tampak pink atau agak pucat, dan "
            "lebih umum pada kulit putih pucat.\n"
            "• Neutral: campuran warm dan cool yang seimbang. Tidak ada rona yang dominan, sehingga "
            "paling fleksibel dalam memilih warna pakaian."
        ),
        "source_note": "Knowledge base internal: knowledge_base_warna_kulit (1).pdf.",
    },
    {
        "code": "SEASONAL_COLOR_TYPE",
        "title": "Apa Itu Seasonal Color Theory?",
        "description": "Sistem empat tipe warna: Spring, Summer, Autumn, dan Winter.",
        "display_order": 3,
        "content": (
            "Seasonal Color Theory adalah sistem yang mengelompokkan orang ke dalam empat tipe warna "
            "berdasarkan musim. Tipe ini ditentukan dari kombinasi undertone dan seberapa cerah atau "
            "dalam kesan penampilan secara keseluruhan.\n\n"
            "Empat tipe utamanya:\n"
            "• Spring: warm undertone, penampilan cerah dan segar. Cocok dengan warna hangat yang "
            "terang seperti coral, peach, dan apricot.\n"
            "• Autumn: warm undertone, penampilan dalam dan earthy. Cocok dengan rust, olive, mustard, "
            "dan terracotta.\n"
            "• Summer: cool undertone, penampilan lembut dan soft. Cocok dengan lavender, dusty rose, "
            "dan powder blue.\n"
            "• Winter: cool undertone, penampilan tegas dan kontras tinggi. Cocok dengan hitam, putih "
            "bersih, navy, dan emerald."
        ),
        "source_note": "Knowledge base internal: knowledge_base_warna_kulit (1).pdf.",
    },
    {
        "code": "DETERMINE_SKIN_TONE",
        "title": "Cara Menentukan Skin Tone",
        "description": "Cara sederhana mengenali skin tone dengan cahaya alami.",
        "display_order": 4,
        "content": (
            "Ikuti langkah-langkah berikut. Cukup butuh cahaya alami.\n\n"
            "1. Cari cahaya alami.\n"
            "Pergi ke dekat jendela atau area outdoor yang tidak terkena sinar matahari langsung. "
            "Hindari lampu ruangan karena cahaya buatan bisa mengubah persepsi warna kulit.\n\n"
            "2. Perhatikan bagian dalam lengan.\n"
            "Lihat bagian dalam pergelangan tangan, bukan punggung tangan. Area ini lebih akurat karena "
            "jarang terpapar sinar matahari langsung.\n\n"
            "3. Bandingkan dengan tiga kategori.\n"
            "• Putih: kulit cerah, ada kesan kemerahan atau pink.\n"
            "• Kuning langsat: kulit terang kekuningan atau gading.\n"
            "• Sawo matang: kulit cokelat medium, terasa hangat atau netral.\n\n"
            "4. Cek respons terhadap matahari sebagai tambahan.\n"
            "Jika kulit langsung jadi cokelat saat terkena matahari, biasanya cenderung kuning langsat "
            "atau sawo matang. Jika mudah memerah atau terbakar, biasanya cenderung putih."
        ),
        "source_note": "Knowledge base internal: knowledge_base_warna_kulit (1).pdf.",
    },
    {
        "code": "DETERMINE_UNDERTONE",
        "title": "Cara Menentukan Undertone",
        "description": "Beberapa tes sederhana untuk memperkirakan undertone.",
        "display_order": 5,
        "content": (
            "Undertone lebih tricky dibanding skin tone. Lakukan minimal 2 dari 3 tes berikut, lalu "
            "lihat hasil mana yang paling konsisten.\n\n"
            "1. Tes urat nadi.\n"
            "Lihat warna urat di bagian dalam pergelangan tangan di bawah cahaya alami.\n"
            "• Hijau atau hijau kekuningan: warm.\n"
            "• Biru atau ungu: cool.\n"
            "• Campuran atau susah ditentukan: neutral.\n\n"
            "2. Tes kertas putih.\n"
            "Tempelkan kertas putih polos di samping wajah tanpa makeup, di cahaya alami.\n"
            "• Kulit terlihat kuning atau peach: warm.\n"
            "• Kulit terlihat pink atau kemerahan: cool.\n"
            "• Tidak ada yang dominan atau terlihat abu-abu: neutral.\n\n"
            "3. Tes perhiasan.\n"
            "Coba emas dan perak secara bergantian, lalu lihat mana yang lebih membuat wajah bercahaya.\n"
            "• Emas lebih flattering: warm.\n"
            "• Perak lebih cocok: cool.\n"
            "• Keduanya sama-sama oke: neutral.\n\n"
            "4. Simpulkan hasilnya.\n"
            "Lihat hasil ketiga tes. Jika satu kategori paling sering muncul, itu kemungkinan "
            "undertone-mu. Jika hasilnya masih campuran atau tidak jelas, kemungkinan besar kamu neutral.\n\n"
            "Setelah tahu undertone, kamu bisa lanjut menentukan seasonal color type dengan melihat "
            "apakah penampilanmu secara keseluruhan lebih cerah seperti Spring/Summer atau lebih "
            "dalam dan kaya seperti Autumn/Winter."
        ),
        "source_note": "Knowledge base internal: knowledge_base_warna_kulit (1).pdf.",
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
