# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Aplikasi Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit
### Mitra Industri: CV Four Vision Media — Seera Project
### Tugas Akhir D3 Teknik Informatika — Politeknik Negeri Bandung (KoTA 103)

---

| Field | Value |
|---|---|
| Kode Proyek | KoTA 103 |
| Versi Dokumen | 2.0 (Final, dengan Modul Multimodal & Alur AIML Lengkap) |
| Tanggal | 2 Mei 2026 |
| Status | Approved for Build (Increment 1) |
| Bahasa | Bahasa Indonesia |
| Kelas Dokumen | Internal — Akademik & Mitra |
| Pemilik Produk | CV Four Vision Media (Seera Project) |
| Pengembang | Tim Mahasiswa D3 TI POLBAN |
| Stack | Vue.js 3 · FastAPI · PostgreSQL · scikit-fuzzy · python-aiml |
| Dependensi Algoritmik | FIS Mamdani (2-layer), RGB→HSV, ROC |
| Out-of-scope | SAW (Simple Additive Weighting) |

---

## TL;DR

- PRD ini mendefinisikan sebuah chatbot edukatif-rekomendatif berbasis **AIML** yang mengubah preferensi natural pengguna (warna kulit, undertone) menjadi **rekomendasi warna pakaian** terurut, melalui **FIS Mamdani 2-layer** (Layer 1: skin_tone × undertone → seasonal type; Layer 2: seasonal × CT × CB produk → suitability score) dipadukan dengan **ROC** untuk produk multi-warna; SAW dikeluarkan dari scope.
- Fokus utama desain percakapan adalah pola AIML idiomatik (`<topic>`, `<that>`, `<srai>`, `<think>`, `<set>/<get>`, `<random>`) untuk mengelola state profiling dan navigasi, dipadu dengan **custom tag multimodal** (`<visual>`, `<palette>`, `<product-card>`, `<chart>`) yang di-parse backend menjadi **blok JSON multimodal** (text/image/palette/product-card/chart) yang ditampilkan oleh frontend Vue.js.
- Output yang harus dihasilkan: chatbot yang ramah, edukatif, dan akurat, mendukung tujuan G1–G7, memiliki dokumentasi spesifikasi algoritma yang lengkap (parameter Fitzpatrick I–VI, Undertone Cool/Neutral/Warm, CT, CB, 18 rules Layer 1, 36 rules Layer 2, contoh perhitungan Navy Blue #1B3A6B, dan ROC), serta skema data PostgreSQL minus `fis_calibration` dan `fis_version`.

---

## Daftar Isi

1. Pendahuluan
2. Gambaran Produk
3. Persona Pengguna
4. Tujuan & Sasaran Produk (G1–G7)
5. Lingkup Fitur (In-Scope / Out-of-Scope)
6. Kebutuhan Fungsional
7. Modul Visualisasi Multimodal AIML *(BARU)*
8. Alur Percakapan AIML *(BARU, hasil riset)*
9. Kebutuhan Non-Fungsional
10. Arsitektur Sistem
11. Spesifikasi Algoritma Detail (A–D)
12. Model Data & ERD
13. Spesifikasi API
14. User Journeys
15. Kriteria Penerimaan
16. Roadmap & Milestone
17. Metrik Keberhasilan
18. Risiko & Mitigasi
19. Asumsi & Batasan
20. Glosarium

---

## 1. Pendahuluan

### 1.1 Tujuan
Dokumen ini mendefinisikan kebutuhan, arsitektur, algoritma, dan kriteria keberhasilan untuk **Aplikasi Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit** sebagai bagian dari Tugas Akhir KoTA 103. PRD menjadi acuan tunggal antara tim pengembang, pembimbing akademik POLBAN, dan mitra industri CV Four Vision Media (Seera Project).

### 1.2 Cakupan
Sistem yang dibangun mencakup: (a) front-end web responsif berbasis Vue.js 3, (b) backend API berbasis FastAPI, (c) basis data PostgreSQL, (d) modul AIML untuk dialog (python-aiml), (e) modul fuzzy Mamdani 2-layer (scikit-fuzzy), (f) modul ROC untuk produk multi-warna, dan (g) lapisan visualisasi multimodal. Cakupan tidak meliputi pengambilan foto wajah otomatis, analisis citra wajah, e-commerce checkout, manajemen inventori real-time, ataupun metode SAW.

### 1.3 Definisi & Akronim
| Istilah | Definisi |
|---|---|
| AIML | Artificial Intelligence Markup Language; XML-based DSL untuk chatbot pattern-matching. |
| FIS | Fuzzy Inference System (Mamdani-type). |
| CT | Color Temperature (turunan Hue HSV). |
| CB | Color Brightness (turunan Value HSV). |
| Y1 | Output Layer-1: Seasonal Color Type (singleton 5/15/20/25). |
| Y2 | Output Layer-2: Suitability Score (singleton 10/35/65/90). |
| ROC | Rank Order Centroid (pembobotan kriteria berbasis ranking). |
| Fitzpatrick | Skala fototipe kulit 6-level (I–VI). |
| Undertone | Hue di bawah permukaan kulit (cool / neutral / warm). |
| Multimodal | Respons chatbot yang menggabungkan teks, gambar, palette, kartu produk, dan chart. |
| Predicate | Slot variabel sesi pada AIML kernel (`<set>`/`<get>`). |
| `<srai>` | Symbolic Reduction in AI; redirect pattern ke pattern lain. |
| `<that>` | Konteks ujaran terakhir bot (untuk dialog context-aware). |
| Topic | Pengelompokan kategori AIML berdasarkan state percakapan. |

### 1.4 Referensi
1. Wallace, R. S. *The Anatomy of A.L.I.C.E.* / *AIML 2.0 Working Draft.*
2. Pandorabots Documentation: AIML Reference & Fundamentals.
3. python-aiml (paulovn/Harmon758) — `SUPPORTED_TAGS.txt`.
4. Jang, J.-S. R., *Neuro-Fuzzy and Soft Computing.*
5. Barron, F. H. & Barrett, B. E. *Decision Quality Using Ranked Attribute Weights.* (ROC)
6. Fitzpatrick, T. B. *The validity and practicality of sun-reactive skin types I through VI.*
7. Itten, J., Carole Jackson — Seasonal Color Theory.
8. Ramli & Kalifia (2025), Butarbutar et al. (2025), Afriyanto & Wibawa (2024) — referensi benchmark internal proposal.
9. WCAG 2.2 — accessibility for conversational interfaces.

---

## 2. Gambaran Produk

### 2.1 Visi Produk
Menjadi **asisten gaya berbasis percakapan** pertama di Indonesia yang memadukan pendekatan **personal color analysis (seasonal)** dengan **logika fuzzy** untuk menghasilkan rekomendasi warna pakaian yang dapat dijelaskan (explainable), inklusif untuk seluruh rentang Fitzpatrick I–VI, dan terintegrasi dengan katalog produk mitra Seera Project.

### 2.2 Latar Belakang Bisnis
CV Four Vision Media (Seera Project) memerlukan diferensiasi pada layanan rekomendasi pakaian yang umumnya berbasis kolaboratif filtering atau like/dislike historis. Pendekatan personal-color-driven memungkinkan rekomendasi yang relevan **tanpa data historis** (cold-start friendly) dan menambah nilai edukatif yang memperkuat brand experience. Industri fashion Indonesia bergeser ke conversational commerce; chatbot personal stylist (mis. Sephora, Klarna) sudah terbukti meningkatkan engagement, sehingga kombinasi AIML + Fuzzy + ROC menawarkan nilai unik (rule-based, interpretable, ringan).

### 2.3 Stakeholders
| Stakeholder | Peran |
|---|---|
| End-User | Konsumen Seera (fashion-conscious, 18–35 tahun). |
| Mitra (CV Four Vision Media) | Pemilik produk, penyedia katalog, validator bisnis. |
| Pembimbing POLBAN | Validator akademik & metodologis. |
| Tim Mahasiswa | Pengembang utama PRD ini. |
| Penguji (Sidang TA) | Evaluator akhir. |

### 2.4 Asumsi Tingkat Tinggi
- Pengguna mengetahui (atau bersedia diajarkan) konsep skin tone & undertone secara sederhana via percakapan.
- Katalog produk mitra menyediakan minimum 1 warna dominan per produk dalam format hex/RGB.
- Lingkungan deploy memiliki Python 3.11+, PostgreSQL 14+, Node 18+.
- Bahasa percakapan default: Bahasa Indonesia (semi-formal, ramah).

---

## 3. Persona Pengguna

### Persona 1 — *Nadya, 23 tahun, Mahasiswi*
- **Goal:** Tahu warna pakaian yang membuatnya “glowing” saat job-fair.
- **Pain point:** Bingung antara warm/cool; sering ragu memilih kemeja.
- **Perilaku:** Suka chatbot di IG; lebih nyaman tap-button daripada mengetik panjang.
- **Kebutuhan kunci:** Edukasi singkat + rekomendasi visual + filter harga.

### Persona 2 — *Bima, 30 tahun, Profesional Muda*
- **Goal:** Membangun capsule wardrobe profesional yang konsisten.
- **Pain point:** Tidak ingin terlihat “mencolok” tapi juga tidak monoton.
- **Perilaku:** Decision-driven, ingin alasan teknis (skor, palette).
- **Kebutuhan kunci:** Score breakdown, palette resmi seasonal type.

### Persona 3 — *Citra, 27 tahun, Content Creator*
- **Goal:** Memilih outfit yang fotogenik di kamera.
- **Pain point:** Hasil tergantung lighting; perlu palette eksperimental.
- **Perilaku:** Visual-first, suka palette grafis yang Instagram-able.
- **Kebutuhan kunci:** Multimodal output (palette + thumbnail + chart).

---

## 4. Tujuan & Sasaran Produk

| Kode | Tujuan | Sasaran Terukur |
|---|---|---|
| **G1** | Chatbot AIML dapat melakukan profiling skin_tone & undertone secara natural. | ≥ 90% sesi profiling berhasil mengisi predicate `skin_tone` dan `undertone`. |
| **G2** | Sistem mampu mengonversi RGB warna produk ke HSV → CT, CB. | Akurasi 100% terhadap kalkulator referensi (toleransi ±0.5°). |
| **G3** | FIS Layer 1 menghasilkan Y1 sesuai 18 rules. | ≥ 95% kesesuaian terhadap manual computation pada test set. |
| **G4** | FIS Layer 2 menghasilkan Y2 sesuai 36 rules. | Defuzzifikasi weighted-average error ≤ 1.0 unit pada test fixture. |
| **G5** | ROC menghasilkan ranking konsisten untuk produk multi-warna. | Σ wᵢ = 1; output ranking deterministik dan reproducible. |
| **G6** | Sistem menyediakan edukasi seasonal color theory yang interaktif. | ≥ 80% pengguna memahami undertone setelah edukasi (uji UX). |
| **G7** | **(BARU)** Chatbot menyajikan respons multimodal (teks + gambar + palette + product-card + chart). | 100% intent kunci memiliki blok visual yang sesuai dan beraksesibilitas WCAG 2.2 AA. |

---

## 5. Lingkup Fitur

### 5.1 In-Scope
- Chatbot AIML berbasis web (Vue.js).
- Modul profiling Fitzpatrick I–VI dan undertone (Cool/Neutral/Warm).
- FIS Mamdani 2-layer (Layer 1, Layer 2).
- ROC untuk produk multi-warna.
- Modul edukasi seasonal color theory.
- Modul rekomendasi produk dengan score & ranking.
- **Modul Visualisasi Multimodal** (custom AIML tags + JSON blocks).
- Modul feedback (thumbs up/down + komentar).
- Manajemen sesi (session token, predicate persistence).

### 5.2 Out-of-Scope
- **SAW (Simple Additive Weighting)** — tidak digunakan.
- Analisis citra wajah otomatis.
- Modul autentikasi/akun lengkap (cukup session token anonim).
- E-commerce checkout, payment gateway, inventory.
- Personalisasi historis lintas-sesi (privacy-first, anonim).
- Notifikasi push, email marketing.

---

## 6. Kebutuhan Fungsional

### 6.1 Modul Chatbot AIML
| ID | Kebutuhan |
|---|---|
| FR-AIML-01 | Sistem harus menerima input teks dan mengembalikan respons sesuai pola AIML. |
| FR-AIML-02 | Sistem harus mengelola state via predicates: `skin_tone`, `undertone`, `seasonal_type`, `last_intent`, `current_topic`, `user_name`. |
| FR-AIML-03 | Sistem harus mendukung sub-modul: **Inisialisasi** (greet, intro), **Profiling** (skin_tone/undertone capture), **Edukasi** (Fitzpatrick, undertone, seasonal theory), **Navigasi** (menu utama, reset, help). |
| FR-AIML-04 | Sistem harus mendukung pattern matching dengan wildcard `*`, `_`, `^`, `#` mengikuti AIML 2.0; prioritas `$` > kata literal > `_` > `*` > `#` (di interpreter yang mendukung). |
| FR-AIML-05 | Sistem harus mendukung `<srai>` untuk simbolik reduksi varian frasa pengguna. |
| FR-AIML-06 | Sistem harus mendukung `<topic>` untuk profiling yang sequential & guarded. |
| FR-AIML-07 | Sistem harus mendukung `<that>` untuk follow-up kontekstual (mis. konfirmasi setelah pertanyaan bot). |
| FR-AIML-08 | Sistem harus memiliki fallback default ketika tidak ada pattern matching, dengan recovery prompt. |

### 6.2 Modul Fuzzy Logic
| ID | Kebutuhan |
|---|---|
| FR-FIS-01 | Konversi RGB → HSV mengikuti rumus standar (lihat A.3). |
| FR-FIS-02 | Layer 1 menerima skin_tone (X1, 1–6) dan undertone (X2) dan menghasilkan Y1 (Seasonal Color Type) via 18 rules (lihat B.2). |
| FR-FIS-03 | Layer 2 menerima Y1, CT, CB produk dan menghasilkan Y2 (Suitability Score 0–100) via 36 rules (lihat C.3). |
| FR-FIS-04 | Defuzzifikasi menggunakan **weighted average** atas singleton output (lihat B.3, C.4). |
| FR-FIS-05 | Sistem harus menangani kondisi Y1 ambigu (dua seasonal aktif, mis. Y1=1.75) tanpa error. |

### 6.3 Modul ROC
| ID | Kebutuhan |
|---|---|
| FR-ROC-01 | Sistem menghitung bobot kriteria via rumus w(k) = (1/n)·Σ(1/j) untuk j=k..n. |
| FR-ROC-02 | Untuk produk dengan n warna terurut (`dominance_rank`), sistem menghitung Skor_Produk = Σ wᵢ · Y2ᵢ. |
| FR-ROC-03 | Bobot harus tersimpan deterministik (tabel bobot n=1, 2, 3 lihat D). |

### 6.4 Modul Manajemen Sesi
| ID | Kebutuhan |
|---|---|
| FR-SES-01 | Setiap pengunjung mendapatkan `session_token` unik (UUIDv4) di first request. |
| FR-SES-02 | Kernel AIML wajib memuat predicate per `session_token`. |
| FR-SES-03 | Sesi memiliki `created_at`, `ended_at` (eksplisit reset atau timeout 30 menit idle). |
| FR-SES-04 | `chat_logs` mencatat tiap turn dengan `intent`, role, content. |

### 6.5 Modul Feedback
| ID | Kebutuhan |
|---|---|
| FR-FB-01 | Setelah recommendation reveal, sistem menampilkan widget thumbs-up/down. |
| FR-FB-02 | Pengguna dapat menambahkan komentar bebas (≤ 500 char). |
| FR-FB-03 | Feedback disimpan terhubung ke `recommendation_id` & `session_id`. |

---

## 7. Modul Visualisasi Multimodal AIML *(BARU)*

### 7.1 Konsep
Karena AIML standar hanya menghasilkan teks, sistem memperluas template AIML dengan **custom tags** yang **tidak melanggar AIML 1.0/2.0** (XML well-formed) tetapi **di-parse di backend** menjadi **blok JSON multimodal** sebelum dikirim ke front-end.

### 7.2 Custom Tags

| Tag | Tujuan | Atribut Utama | Contoh |
|---|---|---|---|
| `<visual>` | Sisipkan ilustrasi/asset visual. | `id`, `alt` | `<visual id="mascot_wave" alt="Maskot Seera melambai"/>` |
| `<palette>` | Tampilkan palette warna. | `season`, `colors` | `<palette season="summer"/>` |
| `<product-card>` | Kartu produk tunggal/grid. | `ids`, `limit`, `score` | `<product-card ids="P12,P34,P55" score="show"/>` |
| `<chart>` | Bar chart skor / breakdown. | `type`, `data` | `<chart type="score-breakdown" data="last_recommendation"/>` |
| `<quick-reply>` | Tombol cepat. | `options` | `<quick-reply options="Cool|Warm|Neutral|Saya tidak tahu"/>` |
| `<fitzpatrick-scale>` | Visual 6-level Fitzpatrick. | `highlight` | `<fitzpatrick-scale highlight="3"/>` |

### 7.3 Format JSON Respons Multimodal
```json
{
  "session_id": "5f9c...uuid",
  "intent": "RECOMMENDATION_REVEAL",
  "blocks": [
    { "type": "text", "content": "Berdasarkan profilmu, kamu termasuk *Summer*." },
    { "type": "palette", "season": "summer",
      "colors": ["#A8C0D6","#7FA4C2","#D5C7E0","#9CAFB7","#F2E8E0"] },
    { "type": "product-card", "items": [
        {"id":"P12","title":"Kemeja Linen Powder Blue","thumb":"...",
         "score":82,"price":"Rp249.000","swatches":["#A8C0D6"]},
        {"id":"P34","title":"Blouse Lavender","thumb":"...",
         "score":78,"price":"Rp199.000","swatches":["#D5C7E0"]}
      ]},
    { "type": "chart", "chart_type":"score-breakdown",
      "data":[{"label":"Y2 Warna 1","value":82},{"label":"ROC w","value":0.61}] },
    { "type": "quick-reply",
      "options":["Filter harga","Lihat lebih banyak","Reset"] }
  ]
}
```

### 7.4 Use Cases per Intent

| Intent | Block Visual |
|---|---|
| Greeting | `text` + `visual(mascot_wave)` + `quick-reply(Mulai|Belajar dulu)` |
| Edukasi Skin Tone | `text` + `fitzpatrick-scale` |
| Edukasi Undertone | `text` + `visual(undertone_warm_cool_neutral_chart)` |
| Edukasi Seasonal | `text` + 4× `palette(spring/summer/autumn/winter)` |
| Profiling Result | `text` + `palette(season)` |
| Recommendation Reveal | `text` + `palette` + `product-card` |
| Score Breakdown | `text` + `chart(score-breakdown)` |
| Feedback Prompt | `text` + `quick-reply(👍|👎)` |

### 7.5 Aksesibilitas (WCAG 2.2 AA)
- Setiap block visual wajib memiliki `alt` atau `aria-label`.
- Kontras teks ≥ 4.5:1; palette swatch disertai label hex untuk tunanetra.
- ARIA-live region pada chat container (`role="log" aria-live="polite"`).
- Quick-reply harus dapat diakses keyboard (Tab + Enter) & screen reader.
- Tidak menggunakan warna sebagai satu-satunya carrier informasi.

### 7.6 Backend Parser (python-aiml + post-processor)
1. AIML kernel menghasilkan respons string (yang masih mengandung XML custom tags).
2. Post-processor (`MultimodalParser`) menggunakan `lxml` / `xml.etree` untuk membongkar respons menjadi list of blocks.
3. Parser meng-resolve `<palette season="x"/>` ke array hex dari tabel `visual_assets`/`colors`.
4. `<product-card ids=...>` di-resolve via service `RecommendationService`.
5. Output final: JSON terstruktur (lihat 7.3) yang dikirim ke front-end.

---

## 8. Alur Percakapan AIML *(BARU)*

### 8.1 Personality & Tone of Voice
- **Nama bot**: “Seera” (selaras dengan brand mitra).
- **Persona**: ramah, supportive, edukatif (mirip personal stylist), tidak preachy.
- **Bahasa**: Indonesia semi-formal, sesekali emoji ringan (✨🎨), kalimat pendek 1–2 baris per bubble.
- **Aturan**: jangan menebak gender, jangan menilai bentuk tubuh, selalu sediakan opsi “Saya tidak tahu”.

### 8.2 Conversation Flow Diagram (End-to-End)

```
                      [START SESSION / OPEN CHAT]
                                  │
                         ┌────────▼────────┐
                         │   GREETING      │   topic=GREETING
                         │  (welcome msg)  │   visual: mascot
                         └────────┬────────┘
                                  │ quick-reply: [Mulai] [Belajar Dulu] [Bantuan]
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
        [EDUKASI MENU]     [PROFILING START]      [HELP]
        Fitzpatrick │            │
        Undertone   │            │ ask skin_tone
        Seasonal    │            │ (Fitzpatrick I-VI)
              │     │            │
              └─────┘            ▼
                          ask undertone
                          (Cool/Neutral/Warm/Idk)
                                  │
                                  ▼
                       [LAYER-1 INFERENCE]
                       skin_tone × undertone → Y1
                                  │
                                  ▼
                     [PROFILING RESULT REVEAL]
                       palette + edukasi season
                                  │
                                  │ quick-reply: [Lihat Rekomendasi] [Refine]
                                  ▼
                     [LAYER-2 + ROC + RANKING]
                                  │
                                  ▼
                  [RECOMMENDATION REVEAL]
                  product-card grid + score
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
              [REFINE]      [SCORE BREAKDOWN]   [FEEDBACK]
            (filter, dll)        chart            👍/👎
                  │               │               │
                  └───────────────┼───────────────┘
                                  ▼
                            [END / RESET]
```

### 8.3 Pattern Matching Strategy
- **Prioritas**: kata literal eksak → `_` (high-priority wildcard) → `*` (default wildcard) → `#` (zero-or-more); `$` digunakan untuk override “sex/jangan tahu” / kata sensitif.
- **Reduksi via `<srai>`**: semua varian sapaan (“halo”, “hai”, “permisi”, “hi”, “assalamualaikum”) → `<srai>GREETING</srai>`.
- **Topic-guarded states**: ketika `topic=PROFILING_SKIN_TONE`, semua input di-route ke kategori dalam topik tsb; pattern `*` di dalam topic menangkap input bebas dan men-`<srai>`-kan ke clarifier.
- **`<that>` checks**: ketika bot bertanya “Apakah kamu cenderung mudah terbakar matahari?”, kategori dengan `<that>APAKAH KAMU CENDERUNG MUDAH TERBAKAR MATAHARI</that>` menangani jawaban “ya/tidak/kadang”.

### 8.4 State Management via Predicates

| Predicate | Tipe | Set di | Get di |
|---|---|---|---|
| `user_name` | string | greeting | personalisasi |
| `skin_tone` | int 1–6 | profiling skin tone | inference Layer 1 |
| `undertone` | enum {cool,neutral,warm} | profiling undertone | inference Layer 1 |
| `seasonal_type` | enum {spring,summer,autumn,winter} | post Layer 1 | reveal & Layer 2 |
| `y1_continuous` | float | post Layer 1 | Layer 2 |
| `last_intent` | string | setiap turn | analytics, fallback |
| `current_topic` | string | tiap topic enter | guard |
| `last_recommendation_id` | int | reveal | feedback, breakdown |

### 8.5 Contoh AIML Code Konkret

**8.5.1 Inisialisasi & Greeting**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<aiml version="2.0">
  <category>
    <pattern>HALO</pattern>
    <template>
      <random>
        <li>Halo! Aku Seera ✨, asisten warna pribadimu.</li>
        <li>Hai! Senang ketemu kamu. Aku Seera 🎨.</li>
      </random>
      <visual id="mascot_wave" alt="Maskot Seera melambai"/>
      Mau aku bantu cari warna pakaian yang paling cocok untukmu?
      <quick-reply options="Mulai Profiling|Belajar Dulu|Apa itu Seera?"/>
      <think><set name="last_intent">GREETING</set></think>
    </template>
  </category>

  <category><pattern>HAI</pattern><template><srai>HALO</srai></template></category>
  <category><pattern>HI</pattern><template><srai>HALO</srai></template></category>
  <category><pattern>HELLO</pattern><template><srai>HALO</srai></template></category>
  <category><pattern>PERMISI</pattern><template><srai>HALO</srai></template></category>
  <category><pattern>ASSALAMUALAIKUM</pattern><template><srai>HALO</srai></template></category>
</aiml>
```

**8.5.2 Onboarding (first-time)**
```xml
<category>
  <pattern>APA ITU SEERA</pattern>
  <template>
    Aku adalah chatbot yang menganalisis warna kulit & undertone kamu,
    lalu merekomendasikan warna pakaian yang paling “glow” untukmu —
    pakai logika fuzzy + teori personal color. Tidak ada foto yang disimpan,
    semua via percakapan saja 🤝
    <quick-reply options="Mulai Profiling|Belajar Dulu"/>
  </template>
</category>
```

**8.5.3 Profiling — Skin Tone (Fitzpatrick)**
```xml
<topic name="PROFILING_SKIN_TONE">
  <category>
    <pattern>*</pattern>
    <that>SEBERAPA MUDAH KULITMU TERBAKAR MATAHARI *</that>
    <template>
      <think>
        <set name="skin_tone_raw"><star/></set>
      </think>
      <srai>RESOLVE SKIN TONE <star/></srai>
    </template>
  </category>
</topic>

<category>
  <pattern>MULAI PROFILING</pattern>
  <template>
    Yuk kita mulai 🌟. Pertama, seberapa mudah kulitmu terbakar saat lama di bawah matahari?
    <quick-reply options="Sangat mudah, langsung memerah|Mudah, jarang cokelat|
        Cukup mudah tapi bisa cokelat|Jarang terbakar, mudah cokelat|
        Sangat jarang terbakar|Hampir tidak pernah terbakar|Saya tidak tahu"/>
    <think>
      <set name="topic">PROFILING_SKIN_TONE</set>
      <set name="last_intent">PROFILING_START</set>
    </think>
  </template>
</category>

<category>
  <pattern>RESOLVE SKIN TONE SANGAT MUDAH *</pattern>
  <template>
    <think><set name="skin_tone">1</set></think>
    Oke, kulit kamu termasuk *Very Fair* (Fitzpatrick I).
    <srai>ASK UNDERTONE</srai>
  </template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE MUDAH JARANG *</pattern>
  <template><think><set name="skin_tone">2</set></think>
  Berarti *Fair* (Fitzpatrick II). <srai>ASK UNDERTONE</srai></template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE CUKUP MUDAH *</pattern>
  <template><think><set name="skin_tone">3</set></think>
  *Medium Fair* (Fitzpatrick III). <srai>ASK UNDERTONE</srai></template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE JARANG TERBAKAR *</pattern>
  <template><think><set name="skin_tone">4</set></think>
  *Moderate Brown* (Fitzpatrick IV). <srai>ASK UNDERTONE</srai></template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE SANGAT JARANG *</pattern>
  <template><think><set name="skin_tone">5</set></think>
  *Brown* (Fitzpatrick V). <srai>ASK UNDERTONE</srai></template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE HAMPIR TIDAK *</pattern>
  <template><think><set name="skin_tone">6</set></think>
  *Dark Brown* (Fitzpatrick VI). <srai>ASK UNDERTONE</srai></template>
</category>
<category>
  <pattern>RESOLVE SKIN TONE SAYA TIDAK *</pattern>
  <template>
    Tenang, aku bantu pakai gambar. <fitzpatrick-scale highlight="0"/>
    Yang mana paling mirip kulitmu?
    <quick-reply options="1|2|3|4|5|6"/>
  </template>
</category>
```

**8.5.4 Profiling — Undertone**
```xml
<category>
  <pattern>ASK UNDERTONE</pattern>
  <template>
    Sekarang, coba lihat urat di pergelangan tanganmu di bawah cahaya alami.
    Warnanya cenderung apa?
    <visual id="vein_test_chart" alt="Ilustrasi tes urat untuk undertone"/>
    <quick-reply options="Biru/Ungu (Cool)|Hijau (Warm)|Campur (Neutral)|Saya tidak tahu"/>
    <think>
      <set name="topic">PROFILING_UNDERTONE</set>
      <set name="last_intent">PROFILING_UNDERTONE</set>
    </think>
  </template>
</category>

<topic name="PROFILING_UNDERTONE">
  <category>
    <pattern>BIRU *</pattern>
    <template>
      <think><set name="undertone">cool</set></think>
      Catat: undertone *Cool* 💙. <srai>RUN LAYER1</srai>
    </template>
  </category>
  <category>
    <pattern>HIJAU *</pattern>
    <template>
      <think><set name="undertone">warm</set></think>
      Catat: undertone *Warm* 🔥. <srai>RUN LAYER1</srai>
    </template>
  </category>
  <category>
    <pattern>CAMPUR *</pattern>
    <template>
      <think><set name="undertone">neutral</set></think>
      Catat: undertone *Neutral* 🌿. <srai>RUN LAYER1</srai>
    </template>
  </category>
  <category>
    <pattern>SAYA TIDAK *</pattern>
    <template>
      Coba cek juga: perhiasan emas atau perak mana yang lebih “nyala” di kulitmu?
      <quick-reply options="Emas (Warm)|Perak (Cool)|Dua-duanya (Neutral)"/>
    </template>
  </category>
</topic>
```

**8.5.5 Trigger Layer-1 → Result Reveal**
```xml
<category>
  <pattern>RUN LAYER1</pattern>
  <template>
    <think><set name="topic">RESULT_REVEAL</set></think>
    Sebentar, aku hitung musim warnamu… ⏳
    <!-- Backend mendeteksi pattern khusus ini, lalu memanggil FIS Layer 1
         dan menyisipkan blok hasil sebelum dikirim ke client. -->
    <visual id="loading_spinner" alt="Memproses"/>
    <srai>REVEAL SEASON <get name="seasonal_type"/></srai>
  </template>
</category>

<category>
  <pattern>REVEAL SEASON SUMMER</pattern>
  <template>
    Hasilnya: kamu *Summer* 🌊 — palette-mu lembut, sejuk, dan elegan.
    <palette season="summer"/>
    Mau lihat rekomendasi pakaian sekarang atau pelajari dulu?
    <quick-reply options="Lihat Rekomendasi|Pelajari Summer|Reset"/>
  </template>
</category>
<category>
  <pattern>REVEAL SEASON SPRING</pattern>
  <template>
    Hasilnya: kamu *Spring* 🌸 — palette warm, cerah, segar.
    <palette season="spring"/>
    <quick-reply options="Lihat Rekomendasi|Pelajari Spring|Reset"/>
  </template>
</category>
<category>
  <pattern>REVEAL SEASON AUTUMN</pattern>
  <template>
    Hasilnya: kamu *Autumn* 🍂 — palette warm, deep, earthy.
    <palette season="autumn"/>
    <quick-reply options="Lihat Rekomendasi|Pelajari Autumn|Reset"/>
  </template>
</category>
<category>
  <pattern>REVEAL SEASON WINTER</pattern>
  <template>
    Hasilnya: kamu *Winter* ❄️ — palette cool, kontras, tegas.
    <palette season="winter"/>
    <quick-reply options="Lihat Rekomendasi|Pelajari Winter|Reset"/>
  </template>
</category>
```

**8.5.6 Edukasi (Seasonal Theory)**
```xml
<category>
  <pattern>BELAJAR DULU</pattern>
  <template>
    Personal color analysis adalah cara mencocokkan warna pakaian dengan
    karakter kulit, mata, dan rambutmu. Ada empat “musim” utama:
    <palette season="spring"/><palette season="summer"/>
    <palette season="autumn"/><palette season="winter"/>
    <quick-reply options="Mulai Profiling|Apa itu Undertone?|Apa itu Skin Tone?"/>
  </template>
</category>

<category>
  <pattern>APA ITU UNDERTONE</pattern>
  <template>
    Undertone itu *warna di bawah permukaan kulit* — tidak berubah
    walau kulit terbakar matahari. Ada tiga: Cool (kebiruan), Warm
    (kekuningan), Neutral (campuran).
    <visual id="undertone_chart" alt="Ilustrasi cool warm neutral undertone"/>
    <quick-reply options="Mulai Profiling|Apa itu Skin Tone?"/>
  </template>
</category>
```

**8.5.7 Recommendation Reveal & Breakdown**
```xml
<category>
  <pattern>LIHAT REKOMENDASI</pattern>
  <template>
    Ini pilihan terbaikku berdasarkan musimmu, dengan skor kecocokan ✨:
    <product-card ids="auto" limit="6" score="show"/>
    <quick-reply options="Filter Harga|Lihat Skor Detail|Beri Feedback|Reset"/>
    <think><set name="last_intent">RECOMMENDATION_REVEAL</set></think>
  </template>
</category>

<category>
  <pattern>LIHAT SKOR DETAIL</pattern>
  <template>
    Berikut breakdown kecocokan warnanya:
    <chart type="score-breakdown" data="last_recommendation"/>
    Skor akhir = Σ wᵢ × Y2ᵢ (ROC). Mau lihat rumusnya?
    <quick-reply options="Ya, jelaskan|Tidak, lanjut"/>
  </template>
</category>
```

**8.5.8 Refinement & Filter**
```xml
<category>
  <pattern>FILTER HARGA</pattern>
  <template>
    Kisaran harga yang kamu mau?
    <quick-reply options="< Rp200k|Rp200k-500k|> Rp500k|Bebas"/>
    <think><set name="topic">FILTER_PRICE</set></think>
  </template>
</category>

<topic name="FILTER_PRICE">
  <category>
    <pattern>_ RP200K</pattern>
    <template>
      <think><set name="filter_price">lt200</set></think>
      Oke, aku saring di bawah Rp200.000.
      <srai>LIHAT REKOMENDASI</srai>
    </template>
  </category>
</topic>
```

**8.5.9 Fallback & Error Handling**
```xml
<category>
  <pattern>*</pattern>
  <template>
    <random>
      <li>Hmm, aku belum paham 🤔. Bisa diulang?</li>
      <li>Maaf, aku belum tangkap maksudmu.</li>
    </random>
    Ini beberapa hal yang bisa aku bantu:
    <quick-reply options="Mulai Profiling|Lihat Rekomendasi|Reset|Bantuan"/>
  </template>
</category>

<category>
  <pattern>RESET</pattern>
  <template>
    <think>
      <set name="skin_tone"></set>
      <set name="undertone"></set>
      <set name="seasonal_type"></set>
      <set name="topic">GREETING</set>
    </think>
    Beres, sesi di-reset ✨. <srai>HALO</srai>
  </template>
</category>
```

**8.5.10 Feedback Collection**
```xml
<category>
  <pattern>BERI FEEDBACK</pattern>
  <template>
    Apakah rekomendasi tadi membantu?
    <quick-reply options="👍 Membantu|👎 Kurang|Beri komentar"/>
    <think><set name="last_intent">FEEDBACK_PROMPT</set></think>
  </template>
</category>

<category>
  <pattern>👍 *</pattern>
  <that>APAKAH REKOMENDASI TADI MEMBANTU</that>
  <template>
    Yay, makasih ya 💖. Mau coba kategori lain atau reset?
    <quick-reply options="Lihat Lebih Banyak|Reset"/>
  </template>
</category>
```

### 8.6 Skenario Dialog Lengkap

**Skenario A — Profiling cepat (Cool / Fitzpatrick III → Summer)**
```
User : halo
Bot  : Halo! Aku Seera ✨ … Mau aku bantu cari warna pakaian yang cocok?
       [Mulai Profiling] [Belajar Dulu] [Apa itu Seera?]
User : Mulai Profiling
Bot  : Yuk kita mulai 🌟. Seberapa mudah kulitmu terbakar matahari?
User : Cukup mudah tapi bisa cokelat
Bot  : *Medium Fair* (Fitzpatrick III). 
       Sekarang, lihat urat di pergelangan tanganmu …
User : Biru/Ungu (Cool)
Bot  : Catat: undertone *Cool* 💙. Sebentar, aku hitung musim warnamu…
Bot  : Hasilnya: kamu *Summer* 🌊
       [palette summer]
User : Lihat Rekomendasi
Bot  : Ini pilihan terbaikku ✨ [product-card x6 with scores]
User : Lihat Skor Detail
Bot  : Berikut breakdown kecocokan warnanya: [chart]
```

**Skenario B — Pengguna tidak tahu undertone**
```
User : Mulai Profiling
Bot  : (skin tone Q)
User : Saya tidak tahu
Bot  : Tenang, aku bantu pakai gambar. [fitzpatrick-scale]
User : 4
Bot  : Oke, *Moderate Brown*. Sekarang undertone … [vein chart]
User : Saya tidak tahu
Bot  : Coba cek juga: emas atau perak yang lebih nyala?
User : Emas
Bot  : Berarti *Warm* 🔥 …
```

**Skenario C — Out of context input**
```
User : kamu bisa pesen makanan?
Bot  : Hmm, aku belum paham 🤔 … aku spesialis warna pakaian.
       [Mulai Profiling] [Lihat Rekomendasi] [Bantuan]
```

**Skenario D — Refinement filter harga**
```
User : Lihat Rekomendasi
Bot  : [grid 6 produk]
User : Filter Harga
Bot  : Kisaran harga …
User : < Rp200k
Bot  : Oke, aku saring di bawah Rp200.000. [grid baru]
```

**Skenario E — Reset di tengah sesi**
```
User : Reset
Bot  : Beres, sesi di-reset ✨. Halo! Aku Seera …
```

---

## 9. Kebutuhan Non-Fungsional

| Aspek | Target |
|---|---|
| **Performa** | P95 latency end-to-end ≤ 1.2 s untuk respons non-rekomendasi; ≤ 2.5 s untuk reveal rekomendasi (≤ 100 produk dievaluasi). |
| **Keandalan** | Uptime ≥ 99% selama jam kerja; graceful degradation (fallback teks-only) jika asset visual gagal load. |
| **Keamanan** | Session token UUIDv4; sanitasi input (XSS-safe); rate limit 60 req/menit/IP; HTTPS wajib; tidak menyimpan PII. |
| **Skalabilitas** | Stateless API (kernel AIML di-instantiate per session, predicate disimpan di DB/Redis); horizontal scale FastAPI worker. |
| **Usability** | SUS score target ≥ 75; ≥ 80% pengguna baru menyelesaikan profiling tanpa bantuan. |
| **Maintainability** | Cakupan unit test ≥ 70%; AIML files modular per topic; FIS rules disimpan terstruktur. |
| **Portabilitas** | Docker compose deploy; OS-agnostic (Linux/macOS/Windows). |
| **Aksesibilitas** | WCAG 2.2 AA. |
| **Privasi** | Anonim by default; logs di-pseudonimkan. |

---

## 10. Arsitektur Sistem

### 10.1 Diagram Tingkat Tinggi (Tekstual)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vue.js 3 + Pinia)                      │
│  ChatWindow │ MessageList(textBlock,palette,productCard,chart) │ QuickReply
│             ▲                                                            │
│             │ JSON multimodal (blocks)                                   │
└─────────────┼────────────────────────────────────────────────────────────┘
              │  REST/WebSocket   (HTTPS)
┌─────────────▼────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Auth/Sess  │  │ Chat Service │  │ Reco Service │  │ Feedback Svc │  │
│  └─────┬──────┘  └─────┬────────┘  └─────┬────────┘  └──────┬───────┘  │
│        │               │                  │                  │           │
│        ▼               ▼                  ▼                  ▼           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │SessionRepo │  │AIML Kernel   │  │FIS Mamdani   │  │ROC Calculator│  │
│  │(Postgres)  │  │(python-aiml) │  │(scikit-fuzzy)│  │(numpy)       │  │
│  └────────────┘  └─────┬────────┘  └─────┬────────┘  └──────┬───────┘  │
│                        ▼                  ▼                  │           │
│                  ┌──────────────┐  ┌──────────────┐          │           │
│                  │MultimodalParser│  │RGB→HSV     │          │           │
│                  └──────────────┘  │CT/CB Mapper  │          │           │
│                                    └──────────────┘          │           │
│                                                              ▼           │
│                          ┌─────────────────────────────────────────┐    │
│                          │          PostgreSQL Database             │    │
│                          │ products, colors, product_colors,        │    │
│                          │ sessions, chat_logs, recommendations,    │    │
│                          │ recommendation_color_scores, feedback,   │    │
│                          │ visual_assets                            │    │
│                          └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Alur Pemrosesan Multimodal (per turn)
1. Frontend kirim `{ session_id, message }` → FastAPI `/chat`.
2. Chat Service: load predicate → AIML Kernel `respond(message)`.
3. Jika respons mengandung pola `RUN LAYER1` → panggil FIS Layer 1; set predicate `seasonal_type`, `y1_continuous`.
4. Jika respons mengandung pola `LIHAT REKOMENDASI` → panggil Reco Service: ambil katalog → Layer 2 per produk per warna → ROC aggregate → ranking top-N.
5. MultimodalParser: parse XML custom tags → resolve ke blok JSON.
6. Kembalikan JSON multimodal ke frontend; tulis `chat_logs` & `recommendations`/`recommendation_color_scores` jika applicable.

---

## 11. Spesifikasi Algoritma Detail

### Bagian A — Definisi Variabel & Parameter

#### A.1 Skin Tone (X1) — Fitzpatrick I–VI
Domain: X1 ∈ [1, 6] (continuous untuk fuzzifikasi).

| Kategori | Fitzpatrick | Bentuk MF | Parameter (a,b,c,d) |
|---|---|---|---|
| Very Fair | I | Trapezoidal | (1.0, 1.0, 1.2, 1.7) |
| Fair | II | Triangular | (1.3, 2.0, 2.7) |
| Medium Fair | III | Triangular | (2.3, 3.0, 3.7) |
| Moderate Brown | IV | Triangular | (3.3, 4.0, 4.7) |
| Brown | V | Triangular | (4.3, 5.0, 5.7) |
| Dark Brown | VI | Trapezoidal | (5.3, 5.8, 6.0, 6.0) |

#### A.2 Undertone (X2)
Domain: X2 ∈ [0, 1] (proxy fuzzy dari klasifikasi user).

| Kategori | Bentuk | Parameter |
|---|---|---|
| Cool | Trapezoidal | (0.00, 0.00, 0.20, 0.40) |
| Neutral | Triangular | (0.30, 0.50, 0.70) |
| Warm | Trapezoidal | (0.60, 0.80, 1.00, 1.00) |

Mapping kategorikal → fuzzy: Cool=0.10, Neutral=0.50, Warm=0.90.

#### A.3 Konversi RGB → HSV (5 Langkah)

Diberikan R,G,B ∈ [0,255]:
1. **Normalisasi**: r = R/255, g = G/255, b = B/255.
2. **Cmax = max(r,g,b); Cmin = min(r,g,b); Δ = Cmax − Cmin.**
3. **Hue (°)**:
   - Jika Δ = 0 → H = 0
   - Jika Cmax = r → H = 60 · (((g−b)/Δ) mod 6)
   - Jika Cmax = g → H = 60 · ((b−r)/Δ + 2)
   - Jika Cmax = b → H = 60 · ((r−g)/Δ + 4)
4. **Saturation**: S = 0 jika Cmax=0; else S = Δ / Cmax.
5. **Value**: V = Cmax.

**Contoh Perhitungan — Navy Blue (#1B3A6B)**
- R=27, G=58, B=107 → r=0.1059, g=0.2275, b=0.4196.
- Cmax = b = 0.4196; Cmin = r = 0.1059; Δ = 0.3137.
- Cmax = b → H = 60·((r−g)/Δ + 4) = 60·((0.1059−0.2275)/0.3137 + 4)
   = 60·(−0.3877 + 4) = 60·3.6123 = **216.7°**.
- S = 0.3137/0.4196 = **0.748**.
- V = **0.4196**.

#### A.4 Color Temperature (CT / X4)
Definisi: kelas CT diturunkan dari Hue.

Zona Hue → kelas:
- **Cool**: 90° ≤ H ≤ 270° (centroid puncak ~210°).
- **Warm**: 0° ≤ H < 60° atau 300° ≤ H < 360°.
- **Neutral (transition)**: 60°–90° dan 270°–300° (zona ambigu).

Untuk fuzzifikasi CT pada domain [0,1] (CT-score, di-mapping dari H):

```
ct_score = 1.0 - cos((H_rad - 30°)/180°·π) / 2 + 0.5
```
*(Implementasi proyek dapat memakai mapping piecewise sederhana berikut.)*

| Kategori CT | Bentuk | Parameter (di domain [0,1]) |
|---|---|---|
| Cool | Trapezoidal | (0.00, 0.00, 0.30, 0.45) |
| Neutral | Triangular | (0.35, 0.50, 0.65) |
| Warm | Trapezoidal | (0.55, 0.70, 1.00, 1.00) |

**Contoh — Navy Blue:** H=216.7° → masuk zona Cool → ct_score ≈ 0.10 → μ_Cool ≈ 1.0; μ_Neutral ≈ 0; μ_Warm ≈ 0.

#### A.5 Color Brightness (CB / X5)
CB = V (HSV value), domain [0,1].

| Kategori CB | Bentuk | Parameter |
|---|---|---|
| Dark | Trapezoidal | (0.00, 0.00, 0.25, 0.40) |
| Medium | Triangular | (0.30, 0.50, 0.70) |
| Light | Trapezoidal | (0.60, 0.75, 1.00, 1.00) |

**Contoh — Navy Blue:** V=0.4196 → μ_Dark ≈ (0.40−0.4196)/(0.40−0.25) = clipped at 0; namun trapezoidal dengan c=0.25, d=0.40 → di V=0.42, kita ambil sisi turun: μ_Dark = max(0, (0.40−0.42)/(0.40−0.25)) = 0; μ_Medium = (0.42−0.30)/(0.50−0.30) = **0.60**; μ_Light = 0. Jadi Navy Blue dominan **Medium**, sedikit ke Dark di area transisi (interpretasi proposal: μ_Dark ≈ 0.0–0.1).

#### A.6 Variabel Output

**Y1 — Seasonal Color Type (singleton)**
| Seasonal | Singleton |
|---|---|
| Spring | 5 |
| Summer | 15 |
| Autumn | 20 |
| Winter | 25 |

Untuk fuzzifikasi Y1 di Layer 2, domain Y1 ∈ [0, 30] dengan MF triangular berpusat pada singleton (lihat C.2).

**Y2 — Suitability Score (singleton, domain [0,100])**
| Kategori | Singleton |
|---|---|
| Not Suitable | 10 |
| Less Suitable | 35 |
| Suitable | 65 |
| Very Suitable | 90 |

---

### Bagian B — FIS Layer 1

#### B.1 Rumus Membership Function

**Triangular** μ(x; a,b,c):
```
μ(x) = 0,                    x ≤ a
       (x-a)/(b-a),          a < x ≤ b
       (c-x)/(c-b),          b < x < c
       0,                    x ≥ c
```

**Trapezoidal** μ(x; a,b,c,d):
```
μ(x) = 0,                    x ≤ a
       (x-a)/(b-a),          a < x < b
       1,                    b ≤ x ≤ c
       (d-x)/(d-c),          c < x < d
       0,                    x ≥ d
```

#### B.2 Aturan Layer 1 (18 Rules)

Notasi: ST = Skin Tone (1–6), UT = Undertone, SCT = Seasonal Color Type, w = bobot pakar.

| # | IF Skin Tone | AND Undertone | THEN Seasonal | Bobot |
|---|---|---|---|---|
| 1 | Very Fair (I) | Cool | Summer | 1.0 |
| 2 | Very Fair (I) | Neutral | Summer | 0.8 |
| 3 | Very Fair (I) | Warm | Spring | 1.0 |
| 4 | Fair (II) | Cool | Summer | 1.0 |
| 5 | Fair (II) | Neutral | Summer | 0.7 |
| 6 | Fair (II) | Warm | Spring | 1.0 |
| 7 | Medium Fair (III) | Cool | Summer | 1.0 |
| 8 | Medium Fair (III) | Neutral | Autumn | 0.6 |
| 9 | Medium Fair (III) | Warm | Spring | 1.0 |
| 10 | Moderate Brown (IV) | Cool | Winter | 0.8 |
| 11 | Moderate Brown (IV) | Neutral | Autumn | 1.0 |
| 12 | Moderate Brown (IV) | Warm | Autumn | 1.0 |
| 13 | Brown (V) | Cool | Winter | 1.0 |
| 14 | Brown (V) | Neutral | Autumn | 0.9 |
| 15 | Brown (V) | Warm | Autumn | 1.0 |
| 16 | Dark Brown (VI) | Cool | Winter | 1.0 |
| 17 | Dark Brown (VI) | Neutral | Winter | 0.8 |
| 18 | Dark Brown (VI) | Warm | Autumn | 0.9 |

#### B.3 Empat Tahap Inferensi Mamdani Layer 1

1. **Fuzzifikasi**: hitung μ_X1(x1) untuk 6 himpunan ST dan μ_X2(x2) untuk 3 himpunan UT.
2. **Evaluasi rule (firing strength)**: untuk tiap rule i, αᵢ = min(μ_X1ᵢ, μ_X2ᵢ) × bobotᵢ.
3. **Agregasi**: kumpulkan αᵢ per kategori SCT (max-aggregate per kelas, atau per rule basis).
4. **Defuzzifikasi (Weighted Average)**:
   ```
   Y1 = Σ (αᵢ · cᵢ) / Σ αᵢ
   ```
   dengan cᵢ = singleton kategori (5/15/20/25).

Hasil Y1 dipetakan ke kategori dominan: Spring (Y1<10), Summer (10≤Y1<17.5), Autumn (17.5≤Y1<22.5), Winter (Y1≥22.5).

---

### Bagian C — FIS Layer 2

#### C.1 Persiapan CT & CB
Untuk tiap warna produk: ambil hex → konversi ke HSV (lihat A.3) → derivasi CT-score & CB-score → fuzzifikasi sesuai A.4 & A.5.

#### C.2 Fuzzifikasi Y1 di Layer 2 (4 himpunan triangular)

| Himpunan Y1 | Triangular (a, b, c) |
|---|---|
| Spring | (0, 5, 10) |
| Summer | (10, 15, 20) |
| Autumn | (15, 20, 25) |
| Winter | (20, 25, 30) |

#### C.3 36 Rules FIS Layer 2 (9 per seasonal)

**Spring (warm-light/medium):**
| # | CT | CB | Y2 |
|---|---|---|---|
| S1 | Warm | Light | Very Suitable |
| S2 | Warm | Medium | Suitable |
| S3 | Warm | Dark | Less Suitable |
| S4 | Neutral | Light | Suitable |
| S5 | Neutral | Medium | Suitable |
| S6 | Neutral | Dark | Less Suitable |
| S7 | Cool | Light | Less Suitable |
| S8 | Cool | Medium | Not Suitable |
| S9 | Cool | Dark | Not Suitable |

**Summer (cool-light/medium):**
| # | CT | CB | Y2 |
|---|---|---|---|
| Su1 | Cool | Light | Very Suitable |
| Su2 | Cool | Medium | Suitable |
| Su3 | Cool | Dark | Less Suitable |
| Su4 | Neutral | Light | Suitable |
| Su5 | Neutral | Medium | Suitable |
| Su6 | Neutral | Dark | Less Suitable |
| Su7 | Warm | Light | Less Suitable |
| Su8 | Warm | Medium | Not Suitable |
| Su9 | Warm | Dark | Not Suitable |

**Autumn (warm-medium/dark):**
| # | CT | CB | Y2 |
|---|---|---|---|
| A1 | Warm | Dark | Very Suitable |
| A2 | Warm | Medium | Very Suitable |
| A3 | Warm | Light | Suitable |
| A4 | Neutral | Dark | Suitable |
| A5 | Neutral | Medium | Suitable |
| A6 | Neutral | Light | Less Suitable |
| A7 | Cool | Dark | Less Suitable |
| A8 | Cool | Medium | Not Suitable |
| A9 | Cool | Light | Not Suitable |

**Winter (cool-medium/dark, kontras tinggi):**
| # | CT | CB | Y2 |
|---|---|---|---|
| W1 | Cool | Dark | Very Suitable |
| W2 | Cool | Medium | Very Suitable |
| W3 | Cool | Light | Suitable |
| W4 | Neutral | Dark | Suitable |
| W5 | Neutral | Medium | Suitable |
| W6 | Neutral | Light | Less Suitable |
| W7 | Warm | Dark | Less Suitable |
| W8 | Warm | Medium | Not Suitable |
| W9 | Warm | Light | Not Suitable |

#### C.4 Empat Tahap Inferensi Layer 2

1. **Fuzzifikasi**: μ_Y1, μ_CT, μ_CB.
2. **Firing strength**: αᵢ = min(μ_CTᵢ, μ_CBᵢ) × μ_Y1(season_of_rule_i).
3. **Agregasi**: per kategori Y2 (Not/Less/Suitable/Very).
4. **Defuzzifikasi (weighted average)**:
   ```
   Y2 = Σ (αᵢ · cᵢ) / Σ αᵢ,   cᵢ ∈ {10, 35, 65, 90}
   ```

#### C.5 Contoh Perhitungan — Pure Summer × Navy Blue

Y1 = 15 (Summer murni) → μ_Spring=0, μ_Summer=1.0, μ_Autumn=0, μ_Winter=0.
Navy: H=216.7° → CT: μ_Cool=1.0, μ_Neutral=0, μ_Warm=0.
V=0.4196 → CB: μ_Medium=0.60, μ_Dark≈0.0, μ_Light=0.

Rule yang aktif (Summer-only):
- Su1 (Cool, Light): α = min(1.0, 0)·1.0 = 0
- Su2 (Cool, Medium): α = min(1.0, 0.60)·1.0 = **0.60** → Suitable (65)
- Su3 (Cool, Dark): α = min(1.0, 0.0)·1.0 = 0

Y2 = (0.60·65) / 0.60 = **65** → Suitable.

**Interpretasi**: Navy Blue *Suitable* untuk Summer murni — masuk akal karena Summer cocok dengan cool tones medium, namun navy yang lebih dark/kontras tinggi sebenarnya lebih ideal untuk Winter.

#### C.6 Contoh — Dua Seasonal Aktif (Y1 = 1.75 representasi Summer-Autumn ambiguity)

*Catatan*: nilai Y1=1.75 di skala internal proposal merepresentasikan transisi Summer→Autumn. Pada skala 0–30 yang dipakai di sini, ekuivalen Y1 ≈ 17.5 (boundary Summer–Autumn).

Y1 = 17.5 → μ_Summer = (20−17.5)/(20−15) = **0.50**; μ_Autumn = (17.5−15)/(20−15) = **0.50**.

Navy: μ_CT_Cool=1.0; μ_CB_Medium=0.60.

Rule aktif:
- Su2 (Cool, Medium → Suitable, 65): α = min(1.0, 0.60)·0.50 = 0.30
- A8 (Cool, Medium → Not Suitable, 10): α = min(1.0, 0.60)·0.50 = 0.30
- (Rule lain dengan μ kecil/0 diabaikan)

Y2 = (0.30·65 + 0.30·10) / (0.30+0.30) = (19.5 + 3.0) / 0.60 = 22.5 / 0.60 = **37.5** → Less Suitable.

#### C.7 Pembahasan Perbandingan

| Skenario | Y1 | Y2 (Navy) | Interpretasi |
|---|---|---|---|
| Pure Summer | 15 | 65 (Suitable) | Cool medium cocok untuk Summer |
| Summer-Autumn ambigu | 17.5 | 37.5 (Less Suitable) | Penalti kuat dari rule Autumn (Cool=NotSuit) |
| (Pure Winter, ilustrasi) | 25 | ~80–90 | Navy ideal untuk Winter (cool, kontras) |

Insight: ketika Y1 ambigu, Y2 turun signifikan, sehingga sistem secara natural mendorong rekomendasi warna lain yang tidak ambigu — meningkatkan akurasi pengalaman.

---

### Bagian D — Rank Order Centroid (ROC)

#### D.1 Rumus Bobot
Untuk n kriteria terurut (k = 1 paling penting):
```
w(k) = (1/n) · Σ_{j=k}^{n} (1/j)
```
Σ w(k) = 1; selalu w(1) ≥ w(2) ≥ … ≥ w(n).

#### D.2 Tabel Bobot Praktis
| n | w₁ | w₂ | w₃ | Σ |
|---|---|---|---|---|
| 1 | 1.000 | — | — | 1.000 |
| 2 | 0.750 | 0.250 | — | 1.000 |
| 3 | 0.611 | 0.278 | 0.111 | 1.000 |

Derivasi n=3:
- w₁ = (1/3)(1/1 + 1/2 + 1/3) = (1/3)(1.8333) = 0.6111
- w₂ = (1/3)(1/2 + 1/3) = (1/3)(0.8333) = 0.2778
- w₃ = (1/3)(1/3) = 0.1111

#### D.3 Skor Produk
```
Skor_Produk = Σᵢ wᵢ · Y2ᵢ
```
dengan Y2ᵢ = skor Layer-2 untuk warna ke-i berdasarkan `dominance_rank`.

#### D.4 Contoh Perhitungan
Produk P12 punya 3 warna dengan Y2 = [82, 68, 40] (urutan dominance):
- Skor_P12 = 0.611·82 + 0.278·68 + 0.111·40 = 50.10 + 18.90 + 4.44 = **73.44**.

Produk P34 punya 2 warna Y2 = [78, 50]:
- Skor_P34 = 0.75·78 + 0.25·50 = 58.50 + 12.50 = **71.00**.

Ranking final: P12 > P34.

---

## 12. Model Data

### 12.1 ERD (Tekstual)

```
categories ──< products ──< product_colors >── colors
                  │              │
                  │              └─ dominance_rank
                  │
sessions ──< chat_logs                          
sessions ──< recommendations ──< recommendation_color_scores >── colors
recommendations ──< feedback
visual_assets (standalone, di-referensi parser)
```

### 12.2 DBML Schema

```dbml
Table categories {
  id          int        [pk, increment]
  name        varchar(80)[not null, unique]
  slug        varchar(80)[not null, unique]
  created_at  timestamptz[default: `now()`]
}

Table products {
  id           int          [pk, increment]
  category_id  int          [ref: > categories.id, not null]
  sku          varchar(64)  [not null, unique]
  title        varchar(160) [not null]
  description  text
  price        numeric(12,2)[not null]
  thumbnail_url varchar(255)
  is_active    boolean      [default: true]
  created_at   timestamptz  [default: `now()`]
  Indexes { (category_id) (is_active) }
}

Table colors {
  id        int         [pk, increment]
  hex       char(7)     [not null, unique, note: "#RRGGBB"]
  name      varchar(80)
  hue       numeric(6,2)
  saturation numeric(5,4)
  value     numeric(5,4)
  ct_score  numeric(5,4)
  cb_score  numeric(5,4)
  Indexes { (hex) }
}

Table product_colors {
  id              int [pk, increment]
  product_id      int [ref: > products.id, not null]
  color_id        int [ref: > colors.id, not null]
  dominance_rank  int [not null, note: "1 = paling dominan"]
  Indexes {
    (product_id, dominance_rank) [unique]
    (color_id)
  }
}

Table sessions {
  id            int          [pk, increment]
  session_token uuid         [not null, unique]
  skin_tone     int          [note: "1..6 Fitzpatrick"]
  undertone     varchar(10)  [note: "cool|neutral|warm"]
  seasonal_type varchar(10)  [note: "spring|summer|autumn|winter"]
  y1_continuous numeric(6,3)
  created_at    timestamptz  [default: `now()`]
  ended_at      timestamptz
  Indexes { (session_token) }
}

Table chat_logs {
  id          bigint       [pk, increment]
  session_id  int          [ref: > sessions.id, not null]
  role        varchar(8)   [note: "user|bot"]
  intent      varchar(40)
  content     jsonb        [not null, note: "blocks multimodal"]
  created_at  timestamptz  [default: `now()`]
  Indexes { (session_id, created_at) (intent) }
}

Table recommendations {
  id            int         [pk, increment]
  session_id    int         [ref: > sessions.id, not null]
  product_id    int         [ref: > products.id, not null]
  roc_score     numeric(7,3)[not null, note: "skor agregat ROC × Y2"]
  final_score   numeric(7,3)[not null]
  rank          int         [not null]
  created_at    timestamptz [default: `now()`]
  Indexes { (session_id, rank) (product_id) }
}

Table recommendation_color_scores {
  id                 bigint [pk, increment]
  recommendation_id  int    [ref: > recommendations.id, not null]
  color_id           int    [ref: > colors.id, not null]
  y2_score           numeric(6,3) [not null]
  roc_weight         numeric(6,4) [not null]
  dominance_rank     int    [not null]
  Indexes { (recommendation_id) }
}

Table feedback {
  id                int          [pk, increment]
  session_id        int          [ref: > sessions.id, not null]
  recommendation_id int          [ref: > recommendations.id]
  rating            varchar(8)   [note: "up|down"]
  comment           varchar(500)
  created_at        timestamptz  [default: `now()`]
  Indexes { (session_id) (recommendation_id) }
}

Table visual_assets {
  id          int          [pk, increment]
  asset_id    varchar(80)  [not null, unique, note: "mascot_wave, undertone_chart, ..."]
  asset_type  varchar(20)  [note: "image|svg|palette|icon"]
  url         varchar(255]
  alt_text    varchar(160) [not null]
  metadata    jsonb
  created_at  timestamptz  [default: `now()`]
}
```

### 12.3 Penjelasan Tabel & Field
- **categories / products**: katalog mitra; `is_active` untuk soft hide.
- **colors**: master warna ter-derivasi (hue/sat/val/ct/cb) sehingga FIS Layer 2 tidak harus menghitung ulang.
- **product_colors**: junction dengan `dominance_rank` untuk ROC.
- **sessions**: anonim, tidak menyimpan `fis_version` (out-of-scope), berisi profiling final.
- **chat_logs**: menyimpan blok JSON multimodal untuk replay/audit.
- **recommendations**: per-sesi, menyimpan `roc_score`, `final_score`, `rank`.
- **recommendation_color_scores**: detail per warna untuk score breakdown chart.
- **feedback**: rating + komentar.
- **visual_assets**: registry asset visual yang di-resolve parser.
- *Tidak digunakan*: `fis_calibration` (logic processing, bukan data).

### 12.4 Indexes & Constraints Kunci
- Unique: `colors.hex`, `categories.slug`, `products.sku`, `sessions.session_token`, `(product_colors.product_id, dominance_rank)`.
- FK ON DELETE CASCADE pada `recommendation_color_scores → recommendations`, `chat_logs → sessions`, `feedback → sessions`.
- Check constraint: `sessions.skin_tone BETWEEN 1 AND 6`; `sessions.undertone IN ('cool','neutral','warm')`.

### 12.5 Data Seed `visual_assets`

```sql
INSERT INTO visual_assets (asset_id, asset_type, url, alt_text) VALUES
('mascot_wave','svg','/assets/mascot/wave.svg','Maskot Seera melambai ramah'),
('mascot_thinking','svg','/assets/mascot/think.svg','Maskot Seera sedang berpikir'),
('fitzpatrick_scale','image','/assets/edu/fitzpatrick.png','Skala Fitzpatrick I-VI berurutan'),
('undertone_chart','image','/assets/edu/undertone.png','Diagram cool, neutral, warm undertone'),
('vein_test_chart','image','/assets/edu/vein_test.png','Ilustrasi tes urat pergelangan tangan'),
('palette_spring','palette','#','Palet Spring: warm light bright',
  '{"colors":["#F4C2A8","#FFD68A","#A8D8B9","#F2A6A6","#FFE9B0"]}'::jsonb),
('palette_summer','palette','#','Palet Summer: cool soft muted',
  '{"colors":["#A8C0D6","#7FA4C2","#D5C7E0","#9CAFB7","#F2E8E0"]}'::jsonb),
('palette_autumn','palette','#','Palet Autumn: warm deep earthy',
  '{"colors":["#B5651D","#8B4513","#C9A66B","#556B2F","#A0522D"]}'::jsonb),
('palette_winter','palette','#','Palet Winter: cool deep contrast',
  '{"colors":["#0B1A3A","#FFFFFF","#B2002D","#5C0A8A","#0B7E66"]}'::jsonb),
('loading_spinner','svg','/assets/ui/spinner.svg','Memproses...');
```

---

## 13. Spesifikasi API

Base URL: `/api/v1`. Konten JSON UTF-8.

### 13.1 `POST /sessions`
Buat sesi anonim baru.
**Response 201**
```json
{ "session_id": 412, "session_token": "5f9c...uuid" }
```

### 13.2 `POST /chat`
Kirim pesan user, terima respons multimodal.
**Request**
```json
{ "session_token": "5f9c...", "message": "halo" }
```
**Response 200**
```json
{
  "intent": "GREETING",
  "blocks": [
    {"type":"text","content":"Halo! Aku Seera ✨ ..."},
    {"type":"visual","asset_id":"mascot_wave","alt":"Maskot Seera melambai"},
    {"type":"quick-reply","options":["Mulai Profiling","Belajar Dulu"]}
  ]
}
```

### 13.3 `GET /profiling/{session_token}`
Ambil snapshot profiling.
**Response 200**
```json
{ "skin_tone": 3, "undertone": "cool", "seasonal_type":"summer",
  "y1_continuous": 14.7 }
```

### 13.4 `POST /recommendations`
Trigger eksplisit (juga ditrigger otomatis oleh AIML pattern).
**Request**
```json
{ "session_token": "5f9c...", "filters": { "price_max": 200000 }, "limit": 6 }
```
**Response 200**
```json
{ "items":[
   {"recommendation_id":901,"product_id":12,"title":"Kemeja Linen Powder Blue",
    "thumb":"...","final_score":73.4,"rank":1,
    "color_breakdown":[
       {"hex":"#A8C0D6","y2":82,"w":0.611,"rank":1},
       {"hex":"#7FA4C2","y2":68,"w":0.278,"rank":2},
       {"hex":"#9CAFB7","y2":40,"w":0.111,"rank":3}
    ]}
]}
```

### 13.5 `GET /visualizations/score-breakdown/{recommendation_id}`
**Response 200**
```json
{ "labels":["Warna 1","Warna 2","Warna 3"],
  "y2":[82,68,40], "w":[0.611,0.278,0.111],
  "final_score":73.4 }
```

### 13.6 `POST /feedback`
**Request**
```json
{ "session_token":"5f9c...","recommendation_id":901,
  "rating":"up","comment":"Pas banget!" }
```
**Response 201** `{ "feedback_id": 55 }`

### 13.7 `POST /sessions/{token}/reset`
Hapus predicate, set `ended_at`, buat sesi baru.

*Tidak ada endpoint terkait SAW.*

---

## 14. User Journeys

### 14.1 Journey A — *Nadya: Profiling Cepat*
1. Buka link → onboarding singkat → tap *Mulai Profiling*.
2. Jawab 2 pertanyaan (skin tone via deskripsi, undertone via vein test).
3. Lihat reveal “Summer” + palette.
4. Tap *Lihat Rekomendasi* → 6 produk dengan skor.
5. Tap 👍.

### 14.2 Journey B — *Bima: Decision-Driven*
1. Tap *Belajar Dulu* → baca seasonal theory.
2. Profiling, hasil “Autumn”.
3. Lihat Rekomendasi.
4. Tap *Lihat Skor Detail* → chart breakdown ROC + Y2.
5. Filter harga > 500k → grid baru.

### 14.3 Journey C — *Citra: Visual-First*
1. Profiling lengkap → “Winter”.
2. Tampilan palette winter + product card grid.
3. Save / screenshot palette → keluar (sesi tersimpan 30 menit).

---

## 15. Kriteria Penerimaan (Acceptance Criteria)

| Modul | Kriteria |
|---|---|
| AIML | Semua 5 skenario dialog (8.6) lulus uji E2E. |
| FIS L1 | Output Y1 sesuai test fixture untuk 18 kombinasi (skin × undertone). |
| FIS L2 | Output Y2 sesuai test fixture untuk 36 kombinasi rule + skenario ambigu. |
| ROC | w(n=1..3) cocok dengan tabel D.2 (toleransi 1e-4). |
| Multimodal | 100% intent kunci punya block visual; alt-text 100%. |
| Aksesibilitas | Audit Lighthouse Accessibility ≥ 95. |
| Performa | P95 chat ≤ 1.2 s, reveal ≤ 2.5 s. |
| Data | Schema migrations idempotent; seed 5 produk × 3 warna sukses. |

---

## 16. Roadmap & Milestone (Februari–Juni 2026)

| Increment | Periode | Cakupan |
|---|---|---|
| **Inc-1: Core Conversational** | Feb–Mar 2026 | Skema DB, AIML greeting/profiling/edukasi, RGB→HSV, FIS Layer 1, Vue prototype, blok teks-only. |
| **Inc-2: Recommendation & Multimodal** | Mar–Apr 2026 | FIS Layer 2, ROC, recommendation reveal, palette + product-card + chart blocks, MultimodalParser. |
| **Inc-3: Polish & UAT** | Apr–Jun 2026 | Filter & refinement, feedback, accessibility audit, performance tuning, docs sidang. |

Sidang TA dijadwalkan akhir Juni 2026.

---

## 17. Metrik Keberhasilan

| Kategori | Metrik | Target |
|---|---|---|
| Adopsi | Jumlah sesi unik / minggu | ≥ 200 (UAT mitra) |
| Engagement | Profiling completion rate | ≥ 80% |
| Akurasi | Kesesuaian Y1 vs ground-truth pakar | ≥ 90% |
| Akurasi | MAE Y2 vs perhitungan manual | ≤ 1.0 |
| Kepuasan | Thumbs-up rate | ≥ 70% |
| Performa | P95 latency | sesuai NFR |
| Aksesibilitas | Lighthouse a11y | ≥ 95 |
| Akademik | Penilaian sidang | ≥ B+ |

---

## 18. Risiko & Mitigasi

| Risiko | Dampak | Likelihood | Mitigasi |
|---|---|---|---|
| AIML kurang fleksibel untuk kalimat bebas | Drop di profiling | Sedang | Banyak `<srai>` reduksi + quick-reply default |
| Klasifikasi undertone subyektif | Akurasi turun | Tinggi | Multi-tes (vein + jewelry + paper); fallback “tidak tahu” → neutral |
| Fitzpatrick eurosentris | Bias di kulit gelap | Sedang | Edukasi spesifik untuk IV–VI; rule terkalibrasi pakar |
| Defuzzifikasi weighted-avg sensitif terhadap rule weight | Output tidak stabil | Sedang | Sensitivity test + dokumentasi parameter |
| Performance reveal lambat untuk katalog besar | UX buruk | Rendah | Pre-compute CT/CB di tabel `colors`; pagination top-N |
| Custom tag merusak XML well-formedness | Parser crash | Rendah | Lint AIML CI; unit test parser |
| Privasi (input bebas) | Kebocoran PII | Rendah | Sanitasi log, retensi 30 hari, anonimisasi |
| Mitra mengubah katalog | Recommendation stale | Sedang | Endpoint admin sync; cache invalidation |

---

## 19. Asumsi & Batasan

- Pengguna jujur dalam profiling (tidak adversarial).
- Bahasa default Indonesia; English hanya pada istilah teknis.
- Tidak ada kanal voice; chat teks-only.
- Maksimum 3 warna dominan diperhitungkan ROC (n ≤ 3); warna ke-4+ diabaikan (mitigasi noise).
- Thresholds ROC dan singleton Y1/Y2 mengikuti proposal akademik (5/15/20/25 dan 10/35/65/90).
- Sistem tidak menggantikan stylist profesional; output bersifat *guidance*.

---

## 20. Glosarium

- **Personal Color Analysis**: praktik mencocokkan warna pakaian dengan karakter natural seseorang.
- **Seasonal Type**: kategori palette (Spring/Summer/Autumn/Winter).
- **Undertone**: hue dasar di bawah permukaan kulit.
- **Hue (H)**: posisi sudut warna pada lingkaran warna (0–360°).
- **Saturation (S)**: intensitas/kemurnian warna.
- **Value (V)**: kecerahan warna pada model HSV.
- **CT (Color Temperature)**: kelas hangat/sejuk turunan dari Hue.
- **CB (Color Brightness)**: kelas terang/gelap turunan dari Value.
- **Mamdani FIS**: tipe FIS dengan output fuzzy → defuzzifikasi crisp.
- **Singleton MF**: MF berbentuk titik tunggal, umumnya untuk output Sugeno-like atau Mamdani simplified.
- **ROC**: Rank Order Centroid, metode pembobotan kriteria berbasis ranking.
- **Predicate (AIML)**: variabel persistensi sesi.
- **`<srai>`**: tag AIML untuk recursion/redirect pattern.
- **`<that>`**: tag AIML untuk kondisi “utterance terakhir bot”.
- **Topic**: kelompok kategori AIML untuk state-aware dialog.
- **Multimodal Block**: unit konten chat (text/image/palette/product-card/chart/quick-reply).
- **WCAG 2.2 AA**: standar aksesibilitas web.

---

## Caveats

- **Parameter membership function** pada bagian A ditampilkan sebagai parameter baseline yang konsisten dengan pendekatan trapezoidal/triangular yang lazim dalam literatur Mamdani; nilai presisi numerik *boleh dikalibrasi ulang* oleh dosen pembimbing/pakar selama bentuk himpunan dan output singleton (5/15/20/25; 10/35/65/90) dipertahankan.
- **Pemetaan H → CT** dapat diimplementasikan piecewise sederhana (tabel zona) atau melalui fungsi cosinus; PRD ini memilih piecewise + trapezoidal di domain [0,1] untuk kemudahan integrasi `scikit-fuzzy`.
- **Skala Fitzpatrick** memiliki keterbatasan inklusivitas yang diakui literatur; sistem mempertahankan I–VI agar konsisten dengan proposal, tetapi roadmap masa depan dapat mengintegrasikan Monk Skin Tone scale (10-level) tanpa mengubah kontrak API.
- Contoh perhitungan untuk **dua seasonal aktif** menggunakan ekuivalensi Y1=17.5 pada skala 0–30 yang setara dengan Y1=1.75 pada skala internal yang lebih ringkas; angka-angka antara dapat berbeda namun *bentuk inferensi tetap valid*.
- **Custom AIML tags** (`<visual>`, `<palette>`, `<product-card>`, `<chart>`, `<quick-reply>`, `<fitzpatrick-scale>`) bukan bagian dari spesifikasi AIML resmi — mereka di-parse oleh post-processor backend dan diabaikan oleh interpreter standar bila tidak ada parser. Hal ini sengaja dipilih karena `python-aiml` (paulovn/Harmon758) bersifat strict 1.0.1 dan tidak meng-eksekusi tag tidak dikenal, sehingga aman.
- **SAW** secara eksplisit dikeluarkan dari scope per arahan; PRD ini tidak menyediakan endpoint, schema, maupun rule SAW.
- Beberapa best-practice UI (typing indicator, ARIA-live, alt text) mengacu pada panduan WCAG 2.2 yang umum berlaku; verifikasi akhir dilakukan via audit Lighthouse + screen-reader manual sebelum sidang.
- Referensi *Ramli & Kalifia (2025), Butarbutar et al. (2025), Afriyanto & Wibawa (2024)* digunakan sebagai konteks benchmarking sesuai brief — angka empiris dari paper-paper tersebut tidak dikutip langsung di PRD ini karena belum diverifikasi independen, tetapi pendekatan FIS Mamdani 2-layer + ROC selaras dengan tradisi metodologi yang mereka gunakan.