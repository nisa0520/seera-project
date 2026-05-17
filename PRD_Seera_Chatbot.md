# PRODUCT REQUIREMENTS DOCUMENT (PRD)

# Aplikasi Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit

**Menggunakan Fuzzy Logic, Rank Order Centroid, Simple Additive Weighting, dan AIML Multimodal**

---

| Atribut Dokumen | Detail |
|---|---|
| **Nama Produk** | Seera Color Match — Chatbot Rekomendasi Warna Pakaian |
| **Kode Proyek** | KoTA 103 |
| **Versi PRD** | 1.0 |
| **Status** | Draft untuk Seminar 2 |
| **Tanggal** | 2 Mei 2026 |
| **Mitra Industri** | CV Four Vision Media (Seera Project) |
| **Institusi** | Politeknik Negeri Bandung — D3 Teknik Informatika |
| **Tim Pengembang** | Aisyah Naomi K. (231511001), Annisa Suci S. (231511005), Timothy Elroy (231511031) |
| **Platform** | Web (Vue.js + FastAPI) |

---

## DAFTAR ISI

1. [Pendahuluan](#1-pendahuluan)
2. [Gambaran Produk](#2-gambaran-produk)
3. [Persona Pengguna](#3-persona-pengguna)
4. [Tujuan dan Sasaran Produk](#4-tujuan-dan-sasaran-produk)
5. [Lingkup Fitur](#5-lingkup-fitur)
6. [Kebutuhan Fungsional](#6-kebutuhan-fungsional)
7. [Modul Visualisasi Multimodal AIML (Fitur Baru)](#7-modul-visualisasi-multimodal-aiml-fitur-baru)
8. [Kebutuhan Non-Fungsional](#8-kebutuhan-non-fungsional)
9. [Arsitektur Sistem](#9-arsitektur-sistem)
10. [Model Data](#10-model-data)
11. [Spesifikasi API](#11-spesifikasi-api)
12. [Perjalanan Pengguna (User Journeys)](#12-perjalanan-pengguna-user-journeys)
13. [Kriteria Penerimaan](#13-kriteria-penerimaan)
14. [Roadmap dan Milestone](#14-roadmap-dan-milestone)
15. [Metrik Keberhasilan](#15-metrik-keberhasilan)
16. [Risiko dan Mitigasi](#16-risiko-dan-mitigasi)
17. [Asumsi dan Batasan](#17-asumsi-dan-batasan)
18. [Glosarium](#18-glosarium)

---

## 1. PENDAHULUAN

### 1.1 Tujuan Dokumen

Dokumen Product Requirements Document (PRD) ini disusun sebagai acuan resmi pengembangan **Aplikasi Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit**. PRD ini menyajikan secara terstruktur kebutuhan fungsional, kebutuhan non-fungsional, arsitektur sistem, model data, serta kriteria penerimaan produk. Dokumen ini ditujukan kepada empat audiens utama: (1) tim pengembang sebagai panduan implementasi, (2) mitra industri CV Four Vision Media sebagai dasar persetujuan ruang lingkup, (3) dosen pembimbing dan penguji sebagai bukti kelengkapan rancangan, serta (4) tim QA dan UAT sebagai sumber rujukan pengujian.

### 1.2 Cakupan Produk

Produk yang dikembangkan adalah **fitur chatbot rekomendasi produk fashion** yang akan diintegrasikan ke dalam platform e-commerce Seera Project milik CV Four Vision Media. Cakupan produk meliputi:

- Antarmuka percakapan interaktif berbasis AIML untuk profiling karakteristik kulit pengguna.
- Mesin perhitungan Fuzzy Inference System (FIS) Mamdani dua-layer untuk menentukan kesesuaian warna.
- Mekanisme pembobotan multi-kriteria dengan Rank Order Centroid (ROC) ketika produk memiliki lebih dari satu warna.
- Perangkingan produk akhir menggunakan Simple Additive Weighting (SAW).
- **Kemampuan baru**: respons multimodal yang menggabungkan teks dan visualisasi (gambar palet warna, kartu produk, infografis edukasi, dan chart skor) dalam satu pesan chatbot.
- Modul edukasi interaktif tentang skin tone, undertone, dan seasonal color theory.

### 1.3 Definisi, Akronim, dan Singkatan

| Singkatan | Kepanjangan |
|---|---|
| AIML | Artificial Intelligence Markup Language |
| FIS | Fuzzy Inference System |
| ROC | Rank Order Centroid |
| SAW | Simple Additive Weighting |
| CT | Color Temperature |
| CB | Color Brightness |
| HSV | Hue, Saturation, Value |
| RGB | Red, Green, Blue |
| MADM | Multi-Attribute Decision Making |
| UAT | User Acceptance Testing |
| ERD | Entity Relationship Diagram |
| API | Application Programming Interface |
| CDN | Content Delivery Network |
| SVG | Scalable Vector Graphics |
| PRD | Product Requirements Document |

### 1.4 Referensi Sumber

- Sommerville, I. (2016). *Software Engineering*, 10th ed.
- Saatchi, R. (2024). Fuzzy Logic Concepts, Development and Implementation. *Information*, 15(10), 656.
- Nasr, T. (2018). Seasonal Color Theory.
- Perrett, D. & Sprengelmeyer, R. (2021). Color Temperature in HSV Space.
- Chernov, V. et al. (2015). RGB-to-HSV Conversion.
- Mahdi, F. et al. (2023). Rank Order Centroid Method.
- Taherdoost, H. (2023). Simple Additive Weighting Method.
- Butarbutar, L. E. et al. (2025). Skinmatch: Rekomendasi Warna Pakaian.
- Ramli, R. & Kalifia, A. D. (2025). Chatbot for Clothing Color Recommendations Based on Skin Tone.
- Afriyanto, A. & Wibawa, Y. E. (2024). Development of Chatbot Services using Fuzzy Logic.
- Zulrahman & Syahputra (2023). AIML.
- Barron, F. H. & Barrett, B. E. (1996). Decision Quality Using Ranked Attribute Weights.
- Fishburn, P. C. (1967). Methods of Estimating Additive Utilities.

---

## 2. GAMBARAN PRODUK

### 2.1 Visi Produk

Menjadi asisten *personal color* berbasis chatbot pertama di platform Seera Project yang membantu setiap pengguna **menemukan warna pakaian yang paling selaras dengan karakteristik kulit mereka**, melalui percakapan natural yang dilengkapi dengan visualisasi yang informatif dan menyenangkan.

### 2.2 Latar Belakang Bisnis

Penelitian Oktaviani & Marsudi (2024) terhadap 135 remaja perempuan Indonesia menemukan bahwa **88,9% responden merasa pakaian yang dikenakan tidak cocok dengan warna kulit mereka**. Sebanyak 61,5% mengetahui adanya seasonal color theory, namun 63,7% di antaranya tidak memahami cara menerapkannya. CV Four Vision Media, melalui Seera Project, mengidentifikasi peluang untuk mengatasi permasalahan ini dengan menghadirkan fitur rekomendasi warna pakaian yang interaktif dan edukatif. Fitur ini diharapkan meningkatkan *conversion rate*, mengurangi *return rate* karena ketidakcocokan warna, dan memperkuat diferensiasi Seera Project dari kompetitor.

### 2.3 Pemangku Kepentingan (Stakeholders)

| Pemangku Kepentingan | Peran | Kepentingan |
|---|---|---|
| CV Four Vision Media | Mitra industri, pemilik platform Seera | Meningkatkan kepuasan pengguna dan diferensiasi produk |
| Pengguna Akhir Seera | Konsumen platform | Mendapat rekomendasi warna yang personal dan akurat |
| Tim Pengembang | Pelaksana proyek tugas akhir | Menyelesaikan TA sesuai standar akademik dan industri |
| Dosen Pembimbing | Penilai akademik | Memastikan kualitas rancangan dan implementasi |
| Tim QA dan UAT mitra | Penguji akhir | Memvalidasi sistem siap operasional |
| Personal Color Analyst (referensi) | Penyedia knowledge base | Menjadi sumber validasi aturan warna |

### 2.4 Asumsi dan Ketergantungan

- Mitra menyediakan akses katalog produk Seera Project (data produk, kategori, harga, rating, popularitas, dan kode HEX warna).
- Platform Seera Project sudah memiliki dasar arsitektur yang siap diintegrasikan dengan modul chatbot via REST API.
- Pengguna mengakses sistem melalui browser web modern (Chrome, Firefox, Safari, Edge versi terbaru).
- Data dummy sintetis (yang dihasilkan AI) dapat digunakan untuk skenario pengujian skala besar.
- Knowledge base seasonal color theory yang digunakan adalah Nasr (2018) dengan empat tipe musim (Spring, Summer, Autumn, Winter) berdasarkan klasifikasi Fitzpatrick (I–VI).

---

## 3. PERSONA PENGGUNA

### 3.1 Persona Utama: Aisha — "Pengguna Pemula Color Theory"

- **Demografi**: Perempuan, 22 tahun, mahasiswa, pengguna aktif e-commerce fashion.
- **Konteks**: Pernah mendengar tentang "warm undertone" dan "cool undertone" tetapi tidak pernah benar-benar memahaminya.
- **Tujuan**: Mengetahui warna pakaian apa yang akan membuat kulitnya terlihat segar dan tidak kusam.
- **Pain Points**: Bingung membaca artikel personal color karena terlalu teknis; pernah salah beli baju yang membuatnya terlihat pucat.
- **Ekspektasi**: Sistem yang ramah, visual, dan tidak mengintimidasi; bisa diajak ngobrol tanpa harus tahu istilah teknis.

### 3.2 Persona Sekunder: Timothy — "Pengguna Praktis"

- **Demografi**: Laki-laki, 28 tahun, pekerja kantoran.
- **Konteks**: Tidak terlalu peduli teori warna; ingin solusi cepat untuk memilih kemeja kerja.
- **Tujuan**: Mendapat tiga sampai lima rekomendasi produk siap-pilih dengan harga terjangkau.
- **Pain Points**: Tidak punya waktu membaca penjelasan panjang.
- **Ekspektasi**: Chatbot yang bisa langsung memberi rekomendasi setelah beberapa pertanyaan singkat, lengkap dengan kartu produk visual.

### 3.3 Persona Tersier: Maya — "Pengguna Antusias Color Analysis"

- **Demografi**: Perempuan, 30 tahun, fashion enthusiast.
- **Konteks**: Sudah tahu seasonal color type dirinya (misalnya "Soft Summer") dan ingin mencari produk yang spesifik sesuai palet.
- **Tujuan**: Mengakses langsung kategori produk dan filter yang sesuai dengan seasonal color type-nya.
- **Pain Points**: Sebagian besar e-commerce tidak menyediakan filter berdasarkan seasonal palette.
- **Ekspektasi**: Chatbot yang menerima input lanjutan ("Saya Soft Summer, cari atasan di bawah Rp 300.000") dan mengembalikan hasil yang akurat dengan visualisasi palet.

---

## 4. TUJUAN DAN SASARAN PRODUK

### 4.1 Tujuan Produk (Product Goals)

| Kode | Tujuan |
|---|---|
| G1 | Aplikasi merekomendasikan warna produk berdasarkan skin tone, undertone, dan seasonal color type pengguna. |
| G2 | Aplikasi menerapkan Fuzzy Logic Mamdani dua-layer untuk menghitung kesesuaian warna produk dengan karakteristik kulit pengguna. |
| G3 | Aplikasi meranking produk menggunakan SAW berdasarkan kesesuaian warna, harga, rating, dan popularitas. |
| G4 | Aplikasi menyediakan chatbot interaktif berbasis AIML untuk memandu rekomendasi. |
| G5 | Aplikasi menyediakan fitur edukatif tentang skin tone, undertone, dan seasonal color type melalui chatbot. |
| G6 | Aplikasi menghasilkan bobot menggunakan Rank Order Centroid (ROC) jika warna produk lebih dari satu. |
| **G7 (Baru)** | **Aplikasi mampu memberikan respons multimodal yang menggabungkan teks dan visualisasi (gambar palet warna, kartu produk, infografis, chart) dalam satu balasan chatbot.** |

### 4.2 Sasaran Bisnis Mitra

- Meningkatkan rata-rata durasi sesi pengguna pada platform Seera minimal **20%** dibandingkan sesi tanpa chatbot.
- Mengurangi tingkat *return rate* karena ketidakcocokan warna minimal **10%** dalam tiga bulan pertama setelah deployment.
- Meningkatkan *click-through rate* dari rekomendasi chatbot ke halaman produk minimal **30%**.

### 4.3 Sasaran Akademik

- Memenuhi seluruh kriteria Tugas Akhir D3 Teknik Informatika Politeknik Negeri Bandung.
- Menyajikan implementasi nyata model Incremental Sommerville (2016).
- Menghasilkan dokumentasi yang dapat dijadikan referensi penelitian lanjutan.

---

## 5. LINGKUP FITUR

### 5.1 Yang Termasuk dalam Lingkup (In-Scope)

1. Modul Chatbot AIML (Inisialisasi, Profiling, Edukasi, Navigasi).
2. Modul Fuzzy Inference System (FIS) Mamdani Layer 1 (input pengguna → seasonal type).
3. Modul Fuzzy Inference System (FIS) Mamdani Layer 2 (warna produk → suitability score).
4. Konversi RGB ↔ HSV dan derivasi nilai CT serta CB.
5. Modul Rank Order Centroid (ROC) untuk pembobotan multi-warna produk.
6. Modul Simple Additive Weighting (SAW) untuk perangkingan akhir.
7. **Modul Visualisasi Multimodal Chatbot** (palet warna, infografis, kartu produk, chart skor).
8. Modul Manajemen Sesi Pengguna (token, riwayat percakapan).
9. Antarmuka frontend Vue.js berbasis chat.
10. REST API backend FastAPI.
11. Skema database PostgreSQL (sesuai ERD pada Bagian 10).
12. Modul Feedback pengguna (rating dan komentar).

### 5.2 Yang Tidak Termasuk dalam Lingkup (Out-of-Scope)

1. Sistem e-commerce penuh (keranjang belanja, checkout, payment gateway).
2. Analisis warna kulit otomatis berbasis kamera atau citra (image-based skin tone detection).
3. Aplikasi mobile native (iOS/Android).
4. Integrasi sistem voice/audio chatbot.
5. Sistem manajemen pengguna dengan autentikasi penuh (login/registrasi). Sesi tetap menggunakan session token tanpa akun pengguna.
6. Multi-bahasa (versi awal hanya Bahasa Indonesia).
7. Sistem pemberitahuan (push notification, email).

---

## 6. KEBUTUHAN FUNGSIONAL

### 6.1 Modul Chatbot AIML

#### 6.1.1 Sub-modul Inisialisasi (Initialization)

| ID | Kebutuhan |
|---|---|
| FR-INIT-01 | Sistem **harus** menampilkan pesan sambutan dengan visual logo Seera ketika pengguna memulai sesi. |
| FR-INIT-02 | Sistem **harus** menyediakan tiga jalur pembuka: (a) "Cari rekomendasi", (b) "Belajar tentang warna kulit saya", dan (c) "Lihat seluruh kategori produk". |
| FR-INIT-03 | Sistem **harus** membuat session token unik dan menyimpan record di tabel `sessions` saat sesi dimulai. |
| FR-INIT-04 | Sistem **harus** menampilkan ringkasan privasi singkat ("Data kamu hanya dipakai untuk menghitung rekomendasi di sesi ini"). |

#### 6.1.2 Sub-modul Profiling

| ID | Kebutuhan |
|---|---|
| FR-PROF-01 | Sistem **harus** mengajukan pertanyaan untuk mengidentifikasi skin tone pengguna berdasarkan skala Fitzpatrick (I–VI). |
| FR-PROF-02 | Sistem **harus** mengajukan pertanyaan untuk mengidentifikasi undertone pengguna (cool/neutral/warm). |
| FR-PROF-03 | Sistem **harus** menerima jawaban berbentuk pilihan visual (button) maupun teks bebas. |
| FR-PROF-04 | Sistem **harus** memvalidasi input dan meminta klarifikasi jika input tidak dapat dipetakan ke nilai numerik. |
| FR-PROF-05 | Sistem **harus** memanggil FIS Layer 1 untuk menghasilkan Y₁ (seasonal color type) setelah skin tone dan undertone diisi. |
| FR-PROF-06 | Sistem **harus** menyimpan hasil profiling (skin_tone, undertone, seasonal_type) ke tabel `sessions`. |
| FR-PROF-07 | Sistem **harus** menampilkan hasil profiling dengan visualisasi palet warna seasonal yang sesuai (lihat Bagian 7). |

#### 6.1.3 Sub-modul Edukasi

| ID | Kebutuhan |
|---|---|
| FR-EDU-01 | Sistem **harus** mampu menjawab pertanyaan "Apa itu skin tone?" dengan teks penjelas dan visual skala Fitzpatrick. |
| FR-EDU-02 | Sistem **harus** mampu menjawab pertanyaan "Apa itu undertone?" dengan teks penjelas dan visual perbandingan warm/cool/neutral. |
| FR-EDU-03 | Sistem **harus** mampu menjawab pertanyaan "Apa itu seasonal color theory?" dengan teks dan visual empat palet musim. |
| FR-EDU-04 | Sistem **harus** menyediakan quick-reply "Pelajari lebih lanjut" pada respons utama untuk masuk ke alur edukasi. |
| FR-EDU-05 | Sistem **harus** menggunakan tag AIML `<srai>` agar variasi pertanyaan ("Beda warm sama cool?", "warm undertone itu apa?") menuju jawaban yang sama. |

#### 6.1.4 Sub-modul Navigasi

| ID | Kebutuhan |
|---|---|
| FR-NAV-01 | Sistem **harus** menyediakan opsi untuk kembali ke menu utama kapan saja. |
| FR-NAV-02 | Sistem **harus** menyediakan opsi "Lihat rekomendasi saya" setelah profiling selesai. |
| FR-NAV-03 | Sistem **harus** menyediakan opsi "Filter berdasarkan kategori" dan "Filter berdasarkan harga" pada hasil rekomendasi. |
| FR-NAV-04 | Sistem **harus** menampilkan breadcrumb percakapan ringkas pada antarmuka. |
| FR-NAV-05 | Sistem **harus** menyediakan opsi reset sesi yang menghapus profil sementara dan memulai ulang. |

### 6.2 Modul Fuzzy Logic

#### 6.2.1 FIS Layer 1 (Profil Pengguna → Seasonal Type)

| ID | Kebutuhan |
|---|---|
| FR-FL1-01 | Sistem **harus** menerima input X₁ (skin tone, universe [1,6]) dan X₂ (undertone, universe [0,2]). |
| FR-FL1-02 | Sistem **harus** memfuzzifikasi X₁ ke enam himpunan: Very Fair, Fair, Medium Fair, Moderate Brown, Brown, Dark Brown. |
| FR-FL1-03 | Sistem **harus** memfuzzifikasi X₂ ke tiga himpunan: Cool, Neutral, Warm. |
| FR-FL1-04 | Sistem **harus** mengevaluasi 18 rules FIS Layer 1 sesuai prinsip Nasr (2018). |
| FR-FL1-05 | Sistem **harus** menggunakan singleton output: Spring=5, Summer=15, Autumn=20, Winter=25. |
| FR-FL1-06 | Sistem **harus** mendefuzzifikasi output dengan metode weighted average sehingga menghasilkan Y₁ kontinu di [0, 3]. |
| FR-FL1-07 | Sistem **harus** menampilkan Y₁ kepada pengguna sebagai label seasonal type (dapat berupa label kompromi seperti "Summer condong ke Autumn"). |

#### 6.2.2 FIS Layer 2 (Warna Produk → Suitability Score)

| ID | Kebutuhan |
|---|---|
| FR-FL2-01 | Sistem **harus** membaca CT dan CB dari tabel `colors` untuk setiap warna produk. |
| FR-FL2-02 | Sistem **harus** memfuzzifikasi Y₁ ke empat himpunan triangular: Spring (0,0.5,1), Summer (0.5,1.5,2), Autumn (1.5,2,2.5), Winter (2,2.5,3). |
| FR-FL2-03 | Sistem **harus** memfuzzifikasi CT ke tiga himpunan (Cool, Neutral, Warm) dengan parameter Trapezoidal/Triangular sesuai Bagian A.4 proposal. |
| FR-FL2-04 | Sistem **harus** memfuzzifikasi CB ke tiga himpunan (Dark, Medium, Light) dengan parameter sesuai Bagian A.5 proposal. |
| FR-FL2-05 | Sistem **harus** mengevaluasi 36 rules FIS Layer 2 dengan formula α = min(μ_CT, μ_CB) × μ_seasonal. |
| FR-FL2-06 | Sistem **harus** menggunakan singleton suitability: Not Suitable=10, Less Suitable=35, Suitable=65, Very Suitable=90. |
| FR-FL2-07 | Sistem **harus** mendefuzzifikasi output Layer 2 dengan weighted average dan menghasilkan Y₂ ∈ [0, 1]. |
| FR-FL2-08 | Sistem **harus** menyimpan nilai Y₂ ke tabel `recommendations` (kolom `fuzzy_score`). |

#### 6.2.3 Konversi RGB-HSV dan Derivasi CT, CB

| ID | Kebutuhan |
|---|---|
| FR-CONV-01 | Sistem **harus** mengkonversi setiap kode HEX warna produk ke RGB (R, G, B ∈ [0, 255]) lalu ke HSV (H ∈ [0°, 360°], S ∈ [0, 1], V ∈ [0, 1]). |
| FR-CONV-02 | Sistem **harus** menghitung CT berdasarkan zona Hue (90°–270° = Cool, 0°–90° dan 270°–360° = Warm) sesuai Perrett & Sprengelmeyer (2021). |
| FR-CONV-03 | Sistem **harus** menetapkan CT = 1.0 (achromatic) jika S = 0. |
| FR-CONV-04 | Sistem **harus** menggunakan V sebagai nilai CB. |
| FR-CONV-05 | Sistem **harus** menyimpan CT dan CB hasil perhitungan ke tabel `colors` saat pendaftaran warna baru. |

### 6.3 Modul Rank Order Centroid (ROC)

| ID | Kebutuhan |
|---|---|
| FR-ROC-01 | Sistem **harus** mengaktifkan modul ROC ketika produk memiliki lebih dari satu warna (`COUNT(product_colors) > 1`). |
| FR-ROC-02 | Sistem **harus** menentukan urutan prioritas warna produk (dominan, sekunder, aksen) berdasarkan urutan penyimpanan di tabel `product_colors`. |
| FR-ROC-03 | Sistem **harus** menghitung bobot ROC sesuai rumus w(k) = (1/n) × Σ(1/j) untuk j = k sampai n. |
| FR-ROC-04 | Sistem **harus** menghitung Skor_Produk = Σ wᵢ × Y₂ᵢ untuk semua warna produk. |
| FR-ROC-05 | Sistem **harus** menyimpan Skor_Produk ke tabel `recommendations` (kolom `roc_score`). |

### 6.4 Modul Simple Additive Weighting (SAW)

| ID | Kebutuhan |
|---|---|
| FR-SAW-01 | Sistem **harus** menggunakan empat kriteria: C1 (Color Suitability Score, benefit, bobot 70), C2 (Harga, cost, bobot 15), C3 (Rating, benefit, bobot 10), C4 (Popularitas, benefit, bobot 5). |
| FR-SAW-02 | Sistem **harus** menormalisasi setiap kriteria dengan rumus: benefit Rᵢⱼ = Xᵢⱼ / max(Xⱼ), cost Rᵢⱼ = min(Xⱼ) / Xᵢⱼ. |
| FR-SAW-03 | Sistem **harus** menghitung Vᵢ = Σ wⱼ × Rᵢⱼ untuk setiap produk. |
| FR-SAW-04 | Sistem **harus** menonaktifkan C2 dan merenormalisasi bobot ke [70, 10, 5] yang dinormalkan ke jumlah 100 jika user tidak mengisi preferensi harga. |
| FR-SAW-05 | Sistem **harus** mengurutkan produk berdasarkan Vᵢ dari yang tertinggi ke terendah dan menyimpan ke tabel `recommendations` (kolom `final_score` dan `rank`). |
| FR-SAW-06 | Sistem **harus** mengembalikan top-N produk (default N=5, bisa diatur 3, 5, atau 10). |

### 6.5 Modul Manajemen Sesi

| ID | Kebutuhan |
|---|---|
| FR-SES-01 | Sistem **harus** membuat session token unik (UUID v4) saat sesi pertama dimulai. |
| FR-SES-02 | Sistem **harus** menyimpan session token di cookie HttpOnly atau localStorage. |
| FR-SES-03 | Sistem **harus** mempertahankan sesi minimal 24 jam sejak interaksi terakhir. |
| FR-SES-04 | Sistem **harus** mencatat setiap pesan ke tabel `chat_logs` dengan field `sender` (user/bot), `message`, dan `created_at`. |
| FR-SES-05 | Sistem **harus** menyediakan endpoint untuk mengambil ulang riwayat percakapan berdasarkan session token. |

### 6.6 Modul Feedback

| ID | Kebutuhan |
|---|---|
| FR-FB-01 | Sistem **harus** menampilkan permintaan feedback (rating 1–5 dan komentar) setelah pengguna melihat hasil rekomendasi. |
| FR-FB-02 | Sistem **harus** menyimpan feedback ke tabel `feedback` dengan referensi ke `sessions.id`. |
| FR-FB-03 | Sistem **harus** mengizinkan pengguna melewatkan tahap feedback. |

---

## 7. MODUL VISUALISASI MULTIMODAL AIML (FITUR BARU)

### 7.1 Latar Belakang Fitur

AIML standar (Zulrahman & Syahputra, 2023) hanya mengembalikan respons teks dari template. Untuk meningkatkan efektivitas edukasi dan rekomendasi, chatbot Seera Color Match perlu mampu **menggabungkan teks dengan visualisasi gambar dalam satu pesan respons**. Riset UX menunjukkan bahwa konsep warna jauh lebih mudah dipahami secara visual daripada deskripsi tekstual semata. Selain itu, kartu produk dengan thumbnail dan swatch warna memberi pengalaman yang lebih dekat dengan e-commerce modern.

Fitur ini melampaui kapabilitas tiga karya ilmiah sejenis yang dikaji dalam proposal: Ramli & Kalifia (2025), Butarbutar et al. (2025), dan Afriyanto & Wibawa (2024) — yang seluruhnya hanya mendukung respons teks. Fitur multimodal ini menjadi salah satu kontribusi utama Tugas Akhir KoTA 103.

### 7.2 Use Cases Visualisasi

| UC-V | Konteks Pemicu | Output Multimodal |
|---|---|---|
| UC-V1 | Pengguna menyelesaikan profiling | Teks: "Kamu cenderung Soft Summer." + Visual: palet warna Summer + label seasonal |
| UC-V2 | Pengguna bertanya "Apa itu undertone?" | Teks: definisi singkat + Visual: infografis perbandingan warm/cool/neutral |
| UC-V3 | Pengguna meminta rekomendasi produk | Teks: "Berikut 5 produk teratas untukmu." + 5 kartu produk visual (thumbnail, swatch warna, harga, rating, skor) |
| UC-V4 | Pengguna bertanya "Kenapa skor produk ini 0.78?" | Teks: penjelasan + Visual: chart bar score breakdown (kontribusi C1, C2, C3, C4) |
| UC-V5 | Pengguna bertanya tentang skin tone | Teks: penjelasan + Visual: skala Fitzpatrick I–VI |
| UC-V6 | Pengguna menerima sambutan awal | Teks: greeting + Visual: ilustrasi maskot Seera |
| UC-V7 | Pengguna meminta visual palette saja | Visual: palet warna seasonal yang sesuai (tanpa teks tambahan) |

### 7.3 Kebutuhan Fungsional Modul Visualisasi

| ID | Kebutuhan |
|---|---|
| FR-VIS-01 | Sistem **harus** mampu mengembalikan respons multimodal yang berisi kombinasi teks dan satu atau lebih komponen visual dalam satu pesan. |
| FR-VIS-02 | AIML template **harus** mendukung custom tag `<visual ref="…"/>` untuk menyisipkan visualisasi statis dari katalog asset. |
| FR-VIS-03 | AIML template **harus** mendukung custom tag `<palette season="…"/>` untuk menampilkan palet warna seasonal. |
| FR-VIS-04 | AIML template **harus** mendukung custom tag `<product-card id="…"/>` untuk menampilkan kartu produk. |
| FR-VIS-05 | AIML template **harus** mendukung custom tag `<chart type="…" data="…"/>` untuk menampilkan grafik dinamis (bar, donut, radar). |
| FR-VIS-06 | Backend **harus** mem-parse template AIML, mendeteksi seluruh custom tag visual, dan mengubahnya menjadi struktur JSON multimodal. |
| FR-VIS-07 | Frontend **harus** menerima payload JSON multimodal dan merender setiap blok teks dan visual sesuai urutan template. |
| FR-VIS-08 | Sistem **harus** mendukung minimal lima jenis visual: (a) palet warna seasonal (Spring/Summer/Autumn/Winter), (b) skala Fitzpatrick, (c) infografis undertone, (d) kartu produk (thumbnail + swatch + metadata), (e) chart skor (breakdown SAW). |
| FR-VIS-09 | Setiap visual **harus** disertai *alt-text* untuk aksesibilitas (WCAG 2.1 Level AA). |
| FR-VIS-10 | Sistem **harus** menyimpan asset statis (palet, infografis) di tabel `visual_assets` dengan field `asset_key` unik. |
| FR-VIS-11 | Sistem **harus** menyimpan setiap pesan multimodal di tabel `chat_logs` dengan field `content_type = 'multimodal'` dan kolom `payload` JSON. |
| FR-VIS-12 | Sistem **harus** graceful-degrade ke teks saja (dengan alt-text) jika gambar gagal di-load di sisi frontend. |
| FR-VIS-13 | Sistem **harus** men-cache visual statis di CDN atau static folder dengan TTL minimal 7 hari. |
| FR-VIS-14 | Visual dinamis (kartu produk, chart) **harus** dirender on-the-fly dari data terkini. Untuk kartu produk, gunakan thumbnail dari `products.thumbnail_url` dan swatch dari `colors.r/g/b`. |
| FR-VIS-15 | Sistem **harus** menyediakan endpoint `GET /api/v1/visuals/{asset_key}` yang mengembalikan metadata dan URL visual statis. |
| FR-VIS-16 | Sistem **harus** menyediakan endpoint `POST /api/v1/charts/score-breakdown` yang menerima `recommendation_id` dan mengembalikan SVG/PNG chart skor. |

### 7.4 Spesifikasi Custom AIML Tags

#### 7.4.1 `<visual ref="..."/>`

Menyisipkan visual statis dari katalog `visual_assets`.

```xml
<category>
  <pattern>APA ITU SKIN TONE</pattern>
  <template>
    Skin tone adalah warna permukaan kulitmu yang dibedakan menjadi enam tipe pada skala Fitzpatrick.
    <visual ref="fitzpatrick_scale"/>
    Coba lihat skala di atas — kamu masuk tipe yang mana?
  </template>
</category>
```

Backend mem-resolve `<visual ref="fitzpatrick_scale"/>` menjadi:

```json
{
  "type": "image",
  "url": "/static/visuals/fitzpatrick_scale.png",
  "alt": "Skala Fitzpatrick: enam tipe warna kulit dari Tipe I (very fair) hingga Tipe VI (dark brown)"
}
```

#### 7.4.2 `<palette season="..."/>`

Menampilkan palet warna untuk tipe seasonal tertentu.

```xml
<category>
  <pattern>TUNJUKKAN PALET SUMMER</pattern>
  <template>
    Berikut palet untuk tipe Summer:
    <palette season="summer"/>
  </template>
</category>
```

Backend mem-resolve menjadi visual palette dengan 12–16 swatch warna khas musim Summer.

#### 7.4.3 `<product-card id="..."/>`

Menampilkan kartu produk individual.

```xml
<category>
  <pattern>REKOMENDASI TERATAS</pattern>
  <template>
    Rekomendasi teratas untukmu:
    <product-card id="*"/>
  </template>
</category>
```

Backend mengambil data produk dari `products` JOIN `colors` JOIN `recommendations`, lalu mengembalikan struktur:

```json
{
  "type": "product-card",
  "data": {
    "product_id": 123,
    "name": "Linen Wrap Top",
    "thumbnail_url": "...",
    "price": 245000,
    "rating": 4.6,
    "score": 0.84,
    "color_swatches": [
      {"name": "Sage Green", "hex": "#9CAF88"},
      {"name": "Ivory", "hex": "#F5F0E1"}
    ]
  }
}
```

#### 7.4.4 `<chart type="..." data="..."/>`

Menampilkan grafik dinamis (bar, donut, radar).

```xml
<category>
  <pattern>JELASKAN SKOR PRODUK *</pattern>
  <template>
    Skor produk ini berasal dari kombinasi empat kriteria:
    <chart type="bar" data="score-breakdown:<star/>"/>
  </template>
</category>
```

Backend menggenerate SVG bar chart yang menampilkan kontribusi C1 (Color Suitability), C2 (Harga), C3 (Rating), dan C4 (Popularitas).

### 7.5 Format Response Multimodal (Backend → Frontend)

Setiap respons chatbot dikirim dalam format JSON berikut:

```json
{
  "session_id": "uuid-...",
  "message_id": 12345,
  "content_type": "multimodal",
  "blocks": [
    { "type": "text", "content": "Kamu cenderung Summer." },
    { "type": "image", "url": "/static/visuals/palette_summer.png",
      "alt": "Palet warna Summer terdiri dari pastel cool seperti soft pink, lavender, dan light blue" },
    { "type": "text", "content": "Mau lihat rekomendasi produk yang cocok dengan palet ini?" }
  ],
  "quick_replies": [
    { "label": "Lihat rekomendasi", "value": "REKOMENDASI" },
    { "label": "Pelajari lebih lanjut", "value": "EDUKASI SUMMER" }
  ],
  "timestamp": "2026-05-02T09:43:11Z"
}
```

### 7.6 Kebutuhan Aksesibilitas

| ID | Kebutuhan |
|---|---|
| FR-A11Y-01 | Setiap visual **harus** memiliki `alt-text` deskriptif (WCAG 2.1 Level AA). |
| FR-A11Y-02 | Kartu produk **harus** dapat dinavigasi dengan keyboard (tab, enter). |
| FR-A11Y-03 | Kontras warna teks pada kartu produk minimal 4.5:1 untuk teks normal. |
| FR-A11Y-04 | Sistem **harus** menyediakan opsi "matikan visual" untuk pengguna dengan koneksi lambat atau pembaca layar. |

---

## 8. KEBUTUHAN NON-FUNGSIONAL

### 8.1 Performa

| ID | Kebutuhan |
|---|---|
| NFR-PERF-01 | Respons chatbot teks **harus** dikembalikan dalam ≤ 800 ms (P95) untuk pesan input ≤ 200 karakter. |
| NFR-PERF-02 | Respons chatbot multimodal **harus** dikembalikan dalam ≤ 1.500 ms (P95). |
| NFR-PERF-03 | Komputasi FIS Mamdani 2-layer untuk satu produk dengan tiga warna **harus** selesai dalam ≤ 50 ms. |
| NFR-PERF-04 | Perangkingan SAW pada 1000 produk **harus** selesai dalam ≤ 500 ms. |
| NFR-PERF-05 | Endpoint API **harus** mendukung minimal 50 concurrent users tanpa degradasi P95 di atas 2 detik. |

### 8.2 Keandalan dan Ketersediaan

| ID | Kebutuhan |
|---|---|
| NFR-REL-01 | Sistem **harus** memiliki uptime ≥ 99% selama jam operasional UAT. |
| NFR-REL-02 | Kegagalan satu komponen visual (misalnya gambar tidak ditemukan) **tidak boleh** menggagalkan seluruh respons. |
| NFR-REL-03 | Sistem **harus** memiliki retry policy 3x untuk kegagalan koneksi database. |

### 8.3 Keamanan

| ID | Kebutuhan |
|---|---|
| NFR-SEC-01 | Session token **harus** disimpan di cookie HttpOnly dan Secure (untuk HTTPS). |
| NFR-SEC-02 | Sistem **harus** menerapkan rate limiting (60 req/menit per session token) pada endpoint chatbot. |
| NFR-SEC-03 | Sistem **harus** memvalidasi dan men-sanitize seluruh input pengguna (mencegah XSS, SQL injection). |
| NFR-SEC-04 | Komunikasi frontend-backend **harus** melalui HTTPS pada deployment produksi. |
| NFR-SEC-05 | Tidak ada Personally Identifiable Information (PII) yang disimpan permanen tanpa persetujuan eksplisit. |

### 8.4 Skalabilitas

| ID | Kebutuhan |
|---|---|
| NFR-SCA-01 | Skema database **harus** mendukung penambahan produk hingga 10.000 tanpa migrasi struktural. |
| NFR-SCA-02 | Modul AIML **harus** mendukung penambahan kategori baru tanpa restart aplikasi. |
| NFR-SCA-03 | Visual statis **harus** di-serve melalui CDN/static folder yang dapat di-scale horizontal. |

### 8.5 Usability

| ID | Kebutuhan |
|---|---|
| NFR-USA-01 | Pengguna pemula **harus** dapat menyelesaikan profiling pertama dalam ≤ 90 detik. |
| NFR-USA-02 | Antarmuka **harus** responsif untuk viewport mobile (320px) hingga desktop (1920px). |
| NFR-USA-03 | Bahasa antarmuka utama adalah Bahasa Indonesia, dengan istilah teknis dalam Bahasa Inggris bila lebih lazim. |
| NFR-USA-04 | Skor System Usability Scale (SUS) target ≥ 75 (rating "Good"). |

### 8.6 Maintainability

| ID | Kebutuhan |
|---|---|
| NFR-MAIN-01 | Kode sumber **harus** mengikuti style guide PEP 8 (Python) dan ESLint Vue 3 default (JavaScript). |
| NFR-MAIN-02 | Setiap modul (AIML, Fuzzy, ROC, SAW, Visual) **harus** terisolasi dengan boundary yang jelas. |
| NFR-MAIN-03 | Coverage unit test minimal 70% untuk modul Fuzzy, ROC, dan SAW. |
| NFR-MAIN-04 | Dokumentasi API **harus** otomatis ter-generate via OpenAPI (FastAPI) dan dapat diakses di endpoint `/docs`. |

### 8.7 Portabilitas dan Kompatibilitas

| ID | Kebutuhan |
|---|---|
| NFR-PORT-01 | Sistem **harus** berjalan pada browser Chrome ≥ 100, Firefox ≥ 100, Safari ≥ 15, Edge ≥ 100. |
| NFR-PORT-02 | Backend **harus** dapat di-deploy via Docker container. |
| NFR-PORT-03 | Database PostgreSQL ≥ 14 dengan dukungan tipe JSON. |

---

## 9. ARSITEKTUR SISTEM

### 9.1 Diagram Arsitektur Tingkat Tinggi

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vue.js 3)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Chat View    │  │ Multimodal   │  │ Static Assets (Visuals)  │   │
│  │ Component    │  │ Renderer     │  │ /static/visuals/         │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────────┘   │
└─────────┼─────────────────┼─────────────────────────────────────────┘
          │ HTTPS / REST    │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │ Chat Router  │  │ Visual       │  │ Recommendation Router    │   │
│  │ /api/v1/chat │  │ Router       │  │ /api/v1/recommendations  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┬───────────┘   │
│         │                 │                         │               │
│  ┌──────┴───────────────────────────────────────────┴───────────┐   │
│  │            ENGINE LAYER                                      │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌──────┐  │   │
│  │  │ AIML     │ │ Fuzzy    │ │ ROC      │ │ SAW    │ │ Vis  │  │   │
│  │  │ Engine   │ │ Engine   │ │ Engine   │ │ Engine │ │ Tag  │  │   │
│  │  │(aiml2)   │ │(scikit-  │ │          │ │        │ │Parser│  │   │
│  │  │          │ │ fuzzy)   │ │          │ │        │ │      │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬───┘ └──┬───┘  │   │
│  └───────┼────────────┼────────────┼────────────┼──────┼───────┘   │
│          │            │            │            │      │           │
│  ┌───────┴────────────┴────────────┴────────────┴──────┴───────┐   │
│  │             DATA ACCESS LAYER (SQLAlchemy ORM)              │   │
│  └───────────────────────────────┬─────────────────────────────┘   │
└──────────────────────────────────┼─────────────────────────────────┘
                                   │
                          ┌────────┴────────┐
                          │ PostgreSQL ≥14  │
                          │ (Seera DB)      │
                          └─────────────────┘
```

### 9.2 Komponen Sistem dan Tanggung Jawabnya

| Komponen | Stack Teknologi | Tanggung Jawab |
|---|---|---|
| **Chat View Component** | Vue.js 3 Composition API | Menampilkan UI chat, mengirim pesan, menerima respons |
| **Multimodal Renderer** | Vue.js 3 + Tailwind | Merender blok teks, gambar, kartu produk, chart sesuai payload |
| **Chat Router** | FastAPI | Endpoint `/api/v1/chat/message` untuk menerima dan memproses input |
| **Visual Router** | FastAPI | Endpoint `/api/v1/visuals/{asset_key}` dan `/api/v1/charts/...` |
| **Recommendation Router** | FastAPI | Endpoint `/api/v1/recommendations` untuk hasil top-N |
| **AIML Engine** | python-aiml / aiml2 | Pattern matching, template processing, custom tag emission |
| **Fuzzy Engine** | scikit-fuzzy | Implementasi FIS Mamdani 2-layer |
| **ROC Engine** | NumPy | Hitung bobot ROC untuk produk multi-warna |
| **SAW Engine** | NumPy | Normalisasi kriteria dan agregasi skor SAW |
| **Visual Tag Parser** | Python + lxml | Mendeteksi `<visual>`, `<palette>`, `<product-card>`, `<chart>` di template AIML dan men-resolve menjadi blok JSON |
| **Data Access Layer** | SQLAlchemy ORM | Akses database via model Python |
| **PostgreSQL** | PostgreSQL ≥14 | Penyimpanan persisten produk, warna, sesi, log, rekomendasi, visual_assets |

### 9.3 Alur Pemrosesan Pesan Multimodal

1. **User mengirim pesan** dari Chat View.
2. **Chat Router** menerima request, memanggil **AIML Engine** dengan input pengguna.
3. **AIML Engine** melakukan pattern matching dan menghasilkan template hasil.
4. **Visual Tag Parser** mengiterasi template:
   - Jika menemukan `<visual ref="..."/>`, query ke `visual_assets` → ambil URL.
   - Jika menemukan `<palette season="..."/>`, lookup palette image.
   - Jika menemukan `<product-card id="..."/>`, query produk + warna + skor.
   - Jika menemukan `<chart type="..." data="..."/>`, generate SVG/PNG.
5. Parser membentuk array `blocks` (urutan teks dan visual sesuai template).
6. Jika template memerlukan rekomendasi (mis. `<product-card id="*"/>`), engine memanggil **Fuzzy Engine + ROC Engine + SAW Engine** secara berurutan.
7. **Chat Router** menyimpan pesan ke `chat_logs` dengan `content_type = 'multimodal'`.
8. **Frontend Multimodal Renderer** menerima JSON dan merender setiap blok.

### 9.4 Diagram Sequence: Permintaan Rekomendasi

```
User → Frontend → Chat API → AIML Engine → Visual Parser → DB
  │       │           │           │              │          │
  │ ketik │           │           │              │          │
  │ "cari │           │           │              │          │
  │ rekom"│           │           │              │          │
  ├──────►│           │           │              │          │
  │       │ POST msg  │           │              │          │
  │       ├──────────►│           │              │          │
  │       │           │ match     │              │          │
  │       │           ├──────────►│              │          │
  │       │           │           │ template ok  │          │
  │       │           │◄──────────┤              │          │
  │       │           │ parse tag │              │          │
  │       │           ├───────────────────────►  │          │
  │       │           │           │              │ SELECT…  │
  │       │           │           │              ├─────────►│
  │       │           │           │              │ products │
  │       │           │           │              │◄─────────┤
  │       │           │ Fuzzy + ROC + SAW        │          │
  │       │           │ (compute scores)         │          │
  │       │           │ JSON multimodal          │          │
  │       │◄──────────┤                          │          │
  │ render│           │                          │          │
  │◄──────┤           │                          │          │
  │ teks  │           │                          │          │
  │ +card │           │                          │          │
```

---

## 10. MODEL DATA

### 10.1 Diagram Entity Relationship (ERD) — Final

ERD final memperluas DBML awal dengan **dua tabel baru** (`visual_assets`, dan field tambahan pada `chat_logs`) untuk mendukung fitur multimodal.

```
categories (id, name)
   │
   │ 1..N
   ▼
products (id, name, price, rating, popularity, stock,
          category_id, thumbnail_url, created_at)
   │                                                 │
   │ N..M (via product_colors)                       │ 1..N
   ▼                                                 ▼
colors (id, color_name, r, g, b, h, s, v, ct, cb)   recommendations
                                                    (id, session_id, product_id,
                                                     fuzzy_score, roc_score,
                                                     final_score, rank, created_at)
                                                       ▲
                                                       │ N..1
                                                       │
sessions (id, session_token, skin_tone, undertone,─────┘
          seasonal_type, created_at)
   │
   ├──── 1..N ──── chat_logs (id, session_id, message,
   │                          sender, content_type,
   │                          payload, created_at)
   │
   └──── 1..N ──── feedback (id, session_id, rating,
                              comment, created_at)

visual_assets (id, asset_key, type, url, alt_text,
               metadata, created_at)
```

### 10.2 Definisi Skema (DBML Final)

```dbml
Table categories {
  id int [pk, increment]
  name varchar
}

Table products {
  id int [pk, increment]
  name varchar
  price float
  rating float
  popularity int
  stock int
  category_id int
  thumbnail_url varchar  // baru, untuk visual product card
  created_at timestamp
}

Table colors {
  id int [pk, increment]
  color_name varchar
  r int
  g int
  b int
  h float
  s float
  v float
  ct float   // 0 to 2 (universe FIS Layer 2)
  cb float   // 0 to 1
}

Table product_colors {
  id int [pk, increment]
  product_id int
  color_id int
  priority int  // baru, untuk urutan ROC (1 = dominan)
}

Table sessions {
  id int [pk, increment]
  session_token varchar [unique]
  skin_tone int          // 1..6 (Fitzpatrick)
  undertone varchar      // 'cool' | 'neutral' | 'warm'
  seasonal_type varchar  // 'spring' | 'summer' | 'autumn' | 'winter' | hybrid label
  y1_value float         // baru, hasil defuzzifikasi FIS Layer 1
  created_at timestamp
}

Table chat_logs {
  id int [pk, increment]
  session_id int
  message text                     // teks plain (untuk pesan user atau ringkasan)
  sender varchar                   // 'user' | 'bot'
  content_type varchar             // baru: 'text' | 'multimodal'
  payload jsonb                    // baru: full multimodal blocks (jika content_type=multimodal)
  created_at timestamp
}

Table recommendations {
  id int [pk, increment]
  session_id int
  product_id int
  fuzzy_score float                // hasil FIS Layer 2 (Y₂ rata-rata atau dominan)
  roc_score float                  // hasil ROC (Skor_Produk / C1)
  final_score float                // hasil SAW (Vᵢ)
  rank int
  created_at timestamp
}

Table feedback {
  id int [pk, increment]
  session_id int
  rating int                       // 1..5
  comment text
  created_at timestamp
}

// === TABEL BARU UNTUK FITUR MULTIMODAL ===

Table visual_assets {
  id int [pk, increment]
  asset_key varchar [unique]       // contoh: 'fitzpatrick_scale', 'palette_summer'
  type varchar                     // 'palette' | 'infographic' | 'icon' | 'illustration'
  url varchar                      // path ke file static
  alt_text varchar                 // teks alternatif untuk aksesibilitas
  metadata jsonb                   // mis. seasonal_type, dimensions, color_count
  created_at timestamp
}

Ref: products.category_id > categories.id
Ref: product_colors.product_id > products.id
Ref: product_colors.color_id > colors.id
Ref: chat_logs.session_id > sessions.id
Ref: recommendations.session_id > sessions.id
Ref: recommendations.product_id > products.id
Ref: feedback.session_id > sessions.id
```

### 10.3 Penjelasan Field Baru

- **`products.thumbnail_url`**: Diperlukan untuk merender thumbnail kartu produk pada respons multimodal.
- **`product_colors.priority`**: Menentukan urutan warna untuk pembobotan ROC (1 = dominan, 2 = sekunder, dst).
- **`sessions.y1_value`**: Menyimpan hasil defuzzifikasi Y₁ (kontinu, bukan label diskrit) sehingga FIS Layer 2 dapat memproses ambiguitas seasonal type.
- **`chat_logs.content_type`**: Membedakan pesan teks murni dengan multimodal.
- **`chat_logs.payload`**: JSON blob berisi struktur multimodal lengkap (untuk replay riwayat percakapan dengan visual).
- **`visual_assets`**: Katalog visual statis (palet, infografis, ikon).

### 10.4 Indeks dan Constraint

| Tabel | Index/Constraint | Tujuan |
|---|---|---|
| `sessions.session_token` | UNIQUE | Mencegah duplikasi token |
| `visual_assets.asset_key` | UNIQUE | Memastikan referensi tag AIML deterministik |
| `recommendations(session_id, product_id)` | UNIQUE | Mencegah duplikasi rekomendasi |
| `chat_logs(session_id, created_at DESC)` | INDEX | Akselerasi query riwayat |
| `products.category_id` | FOREIGN KEY | Integritas referensial |

### 10.5 Data Seed (Visual Assets Awal)

| asset_key | type | deskripsi |
|---|---|---|
| `fitzpatrick_scale` | infographic | Visual enam tipe kulit Fitzpatrick I–VI |
| `undertone_comparison` | infographic | Perbandingan warm vs cool vs neutral |
| `palette_spring` | palette | 16 swatch warna khas Spring |
| `palette_summer` | palette | 16 swatch warna khas Summer |
| `palette_autumn` | palette | 16 swatch warna khas Autumn |
| `palette_winter` | palette | 16 swatch warna khas Winter |
| `seasonal_overview` | infographic | Diagram 4 musim dalam satu gambar |
| `mascot_seera` | illustration | Maskot ilustrasi Seera untuk pesan sambutan |
| `fuzzy_membership_demo` | infographic | Visualisasi konsep derajat keanggotaan |
| `rgb_to_hsv_diagram` | infographic | Diagram konversi ruang warna |

---

## 11. SPESIFIKASI API

### 11.1 Konvensi Umum

- **Base URL**: `/api/v1`
- **Format**: JSON (Content-Type: `application/json`)
- **Autentikasi**: Session token via cookie HttpOnly atau header `X-Session-Token`
- **Versioning**: URL-based (`/v1/`)

### 11.2 Endpoint: Chat

#### POST `/api/v1/chat/session`
Membuat sesi baru.
- **Request**: `{ }`
- **Response 201**:
```json
{ "session_token": "uuid-v4", "expires_at": "2026-05-03T09:43:11Z" }
```

#### POST `/api/v1/chat/message`
Mengirim pesan ke chatbot.
- **Headers**: `X-Session-Token: <token>`
- **Request**:
```json
{ "message": "apa itu undertone" }
```
- **Response 200** (multimodal):
```json
{
  "session_id": "uuid",
  "message_id": 12345,
  "content_type": "multimodal",
  "blocks": [
    { "type": "text", "content": "Undertone adalah warna dasar kulit yang…" },
    { "type": "image", "url": "/static/visuals/undertone_comparison.png",
      "alt": "Perbandingan undertone warm, cool, dan neutral" },
    { "type": "text", "content": "Mau cek undertone-mu sekarang?" }
  ],
  "quick_replies": [
    { "label": "Ya, cek sekarang", "value": "MULAI PROFILING" },
    { "label": "Pelajari lagi", "value": "EDUKASI LANJUTAN" }
  ],
  "timestamp": "2026-05-02T09:43:11Z"
}
```

#### GET `/api/v1/chat/history`
Mengambil riwayat percakapan sesi aktif.
- **Headers**: `X-Session-Token`
- **Response**: array `chat_logs`.

### 11.3 Endpoint: Profiling

#### POST `/api/v1/profile/skin-tone`
- **Body**: `{ "skin_tone": 3 }` (1..6)
- **Response**: `{ "ok": true }`

#### POST `/api/v1/profile/undertone`
- **Body**: `{ "undertone": "cool" }`
- **Response**: `{ "ok": true }`

#### POST `/api/v1/profile/compute-seasonal`
Memicu FIS Layer 1.
- **Response**:
```json
{
  "y1_value": 1.75,
  "seasonal_label": "Summer condong ke Autumn",
  "memberships": { "spring": 0, "summer": 0.5, "autumn": 0.5, "winter": 0 }
}
```

### 11.4 Endpoint: Recommendation

#### GET `/api/v1/recommendations?top_n=5&include_price_pref=true`
- **Headers**: `X-Session-Token`
- **Response**:
```json
{
  "session_id": "uuid",
  "items": [
    {
      "rank": 1,
      "product_id": 42,
      "name": "Linen Wrap Top",
      "thumbnail_url": "...",
      "price": 245000,
      "rating": 4.6,
      "fuzzy_score": 0.81,
      "roc_score": 0.78,
      "final_score": 0.84,
      "color_swatches": [
        { "color_id": 9, "name": "Sage Green", "hex": "#9CAF88" },
        { "color_id": 14, "name": "Ivory White", "hex": "#F5F0E1" }
      ]
    }
  ]
}
```

### 11.5 Endpoint: Visualization

#### GET `/api/v1/visuals/{asset_key}`
- **Response 200**:
```json
{
  "asset_key": "palette_summer",
  "type": "palette",
  "url": "/static/visuals/palette_summer.png",
  "alt": "Palet warna Summer terdiri dari pastel cool…",
  "metadata": { "seasonal_type": "summer", "color_count": 16 }
}
```

#### POST `/api/v1/charts/score-breakdown`
- **Body**: `{ "recommendation_id": 555 }`
- **Response 200** (image/svg+xml atau JSON dengan data):
```json
{
  "type": "chart",
  "format": "svg",
  "url": "/api/v1/charts/score-breakdown/555.svg",
  "alt": "Bar chart skor: Color Suitability 0.81, Harga 0.7, Rating 0.92, Popularitas 0.65",
  "data": {
    "C1": 0.81, "C2": 0.70, "C3": 0.92, "C4": 0.65
  }
}
```

### 11.6 Endpoint: Feedback

#### POST `/api/v1/feedback`
- **Body**: `{ "rating": 5, "comment": "Sangat membantu!" }`
- **Response**: `{ "ok": true }`

### 11.7 Error Handling

| HTTP Code | Skenario |
|---|---|
| 400 | Input tidak valid (skin_tone di luar [1,6], dsb) |
| 401 | Session token tidak ada / kedaluwarsa |
| 404 | Asset / produk tidak ditemukan |
| 429 | Rate limit terlampaui |
| 500 | Kesalahan server internal |

Format error standar:
```json
{ "error": { "code": "INVALID_INPUT", "message": "Skin tone harus 1-6" } }
```

---

## 12. PERJALANAN PENGGUNA (USER JOURNEYS)

### 12.1 Journey 1: Pengguna Baru — End-to-End Rekomendasi

| Step | User Action | System Response |
|---|---|---|
| 1 | Buka aplikasi Seera Color Match | Tampilkan greeting + ilustrasi maskot + tiga jalur pembuka |
| 2 | Tap "Cari rekomendasi" | Sistem: "Mulai dengan profil dulu ya. Pertama, gimana warna kulitmu?" + visual skala Fitzpatrick |
| 3 | Tap pilihan tipe III | Sistem: "Sip, kulit medium fair. Sekarang, undertone-mu cool, neutral, atau warm?" + visual perbandingan |
| 4 | Tap "Neutral" | Sistem: panggil FIS Layer 1 → "Kamu cenderung Spring." + palette Spring |
| 5 | Tap "Lihat rekomendasi" | Sistem: panggil pipeline (FIS L2 + ROC + SAW) → 5 kartu produk dengan thumbnail, swatch, harga, rating, skor |
| 6 | Tap kartu produk #1 | Sistem: tampilkan detail + bar chart skor breakdown |
| 7 | Tap "Beri rating sesi ini" | Sistem: tampilkan widget rating 1-5 dan komentar |
| 8 | Submit feedback | Sistem: "Terima kasih! Sampai jumpa lagi." + simpan feedback |

### 12.2 Journey 2: Pengguna Edukatif

| Step | User Action | System Response |
|---|---|---|
| 1 | Tap "Belajar tentang warna kulit" | Tampilkan 3 topik: Skin Tone, Undertone, Seasonal Color Theory |
| 2 | Tap "Skin Tone" | Teks penjelasan + visual Fitzpatrick + quick reply "Cek skin tone-ku" |
| 3 | Tap "Cek skin tone-ku" | Lanjut alur Profiling |

### 12.3 Journey 3: Pengguna Lanjutan dengan Filter

| Step | User Action | System Response |
|---|---|---|
| 1 | Ketik "saya soft summer, cari atasan di bawah 300rb" | Sistem parse intent → set seasonal=summer, kategori=atasan, max_price=300000 |
| 2 | — | Sistem panggil pipeline dengan filter → 5 kartu produk yang memenuhi |
| 3 | Tap "Filter rating ≥ 4.5" | Sistem refine list → tampilkan ulang |

---

## 13. KRITERIA PENERIMAAN

### 13.1 Kriteria Penerimaan Tingkat Produk

- AC-PROD-01: Sistem berhasil memproses minimal 100 sesi pengujian tanpa kegagalan kritis.
- AC-PROD-02: Mitra CV Four Vision Media menyetujui hasil UAT pada Iterasi 3.
- AC-PROD-03: Skor SUS dari 10+ partisipan pengujian usability ≥ 75.

### 13.2 Kriteria Penerimaan per Modul Utama

#### Modul Fuzzy Logic
- AC-FL-01: Y₁ dan Y₂ untuk minimal 10 skenario uji konsisten dengan perhitungan manual (toleransi ±0.01).
- AC-FL-02: Skenario "ambiguitas Summer-Autumn" (Y₁=1.75) menghasilkan derajat keanggotaan kedua sama (0.5/0.5).

#### Modul ROC
- AC-ROC-01: Bobot untuk produk 3 warna sesuai tabel: w₁=0.611, w₂=0.278, w₃=0.111 (toleransi ±0.001).
- AC-ROC-02: Bobot menjumlah 1.0 untuk berapapun n.

#### Modul SAW
- AC-SAW-01: Top-1 produk dari 100 produk uji konsisten dengan perhitungan manual.
- AC-SAW-02: Renormalisasi bobot tanpa C2 menghasilkan total 100.

#### Modul Visualisasi Multimodal (Fitur Baru)
- AC-VIS-01: Sistem mengembalikan respons multimodal valid untuk minimal 10 use case berbeda.
- AC-VIS-02: Setiap visual memiliki alt-text non-kosong.
- AC-VIS-03: Frontend merender blok teks dan visual sesuai urutan template AIML pada minimal 3 browser modern.
- AC-VIS-04: Graceful degradation aktif: ketika URL gambar di-block, alt-text tetap ditampilkan dan layout tidak rusak.
- AC-VIS-05: Kartu produk menampilkan minimal: thumbnail, nama, harga, rating, skor akhir, dan minimal 1 swatch warna dominan.
- AC-VIS-06: Chart score-breakdown akurat menampilkan kontribusi setiap kriteria SAW.

---

## 14. ROADMAP DAN MILESTONE

### 14.1 Ringkasan Roadmap (Februari–Juni 2026)

| Periode | Milestone | Deliverable |
|---|---|---|
| Feb Mg1 – Mar Mg2 | Pendefinisian dan Studi Literatur | Proposal TA, Bab I–III Laporan |
| Mar Mg3 | Seminar 1 (Proposal) | Slide proposal, dokumen revisi |
| Mar Mg4 – Apr Mg3 | **Increment 1 — Modul Dasar** | AIML Inisialisasi & Profiling, FIS Mamdani 2-layer, antarmuka awal Vue.js, REST API skeleton |
| Apr Mg4 | **Seminar 2** (Release 1) | Demo Increment 1, dokumen revisi |
| Mei Mg1 – Mg3 | **Increment 2 — Integrasi & Penyempurnaan** | ROC, AIML Edukasi & Navigasi, **Modul Visualisasi Multimodal**, kartu produk, integration testing |
| Mei Mg4 | **Seminar 3** (Release 2) | Demo Increment 2, dokumen revisi |
| Jun Mg1 – Mg3 | **Increment 3 — Pengujian & Finalisasi** | UAT bersama mitra, perbaikan defek, dokumentasi final |
| Jun Mg4 | **Sidang TA** | Sistem final, laporan TA lengkap, presentasi |

### 14.2 Penempatan Fitur Visualisasi Multimodal

Fitur multimodal masuk ke **Increment 2 (Mei 2026)** sebagai bagian dari "Integrasi & Penyempurnaan", dengan dependency pada modul AIML dan Fuzzy yang sudah selesai di Increment 1.

| Sub-task Increment 2 | Estimasi Effort |
|---|---|
| Desain skema `visual_assets` dan migrasi DB | 2 hari |
| Implementasi Visual Tag Parser (backend) | 4 hari |
| Implementasi Multimodal Renderer (frontend) | 4 hari |
| Produksi 10 visual seed (palet, infografis, ilustrasi) | 5 hari (paralel) |
| Implementasi endpoint `/api/v1/visuals` & `/api/v1/charts` | 3 hari |
| Integrasi `<product-card>` dengan pipeline rekomendasi | 3 hari |
| Pengujian unit + integration multimodal | 3 hari |
| Total estimasi | ~24 person-day (paralel di 3 anggota tim) |

### 14.3 Rilis

- **Release 1** (akhir Increment 1): Antarmuka chat berbasis teks, FIS Mamdani 2-layer, profiling.
- **Release 2** (akhir Increment 2): + ROC, SAW, Edukasi, **Visualisasi Multimodal**.
- **Release 3** (akhir Increment 3): Sistem final, sudah lulus UAT, dokumentasi siap-cetak.

---

## 15. METRIK KEBERHASILAN

### 15.1 Metrik Produk

| Metrik | Target |
|---|---|
| Tingkat penyelesaian profiling (profiling completion rate) | ≥ 80% |
| Click-through rate dari kartu rekomendasi ke detail produk | ≥ 30% |
| Rerata rating sesi (1–5) | ≥ 4.0 |
| Skor SUS | ≥ 75 |
| Time-to-recommendation (dari greeting ke top-N) | ≤ 90 detik untuk pemula |

### 15.2 Metrik Teknis

| Metrik | Target |
|---|---|
| Akurasi FIS terhadap perhitungan manual | ≥ 99% (10 skenario uji) |
| Latensi P95 chat teks | ≤ 800 ms |
| Latensi P95 chat multimodal | ≤ 1.500 ms |
| Coverage unit test | ≥ 70% |
| Uptime selama UAT | ≥ 99% |

### 15.3 Metrik Bisnis (untuk Mitra)

| Metrik | Target |
|---|---|
| Peningkatan rerata durasi sesi platform Seera | ≥ 20% |
| Penurunan return rate karena ketidakcocokan warna | ≥ 10% |
| Peningkatan engagement edukasi (% pengguna yang mengakses modul edukasi) | ≥ 25% |

---

## 16. RISIKO DAN MITIGASI

| ID | Risiko | Dampak | Probabilitas | Mitigasi |
|---|---|---|---|---|
| R1 | Knowledge base seasonal color theory tidak akurat untuk subjek Asia | Tinggi | Sedang | Validasi rule fuzzy dengan referensi Butarbutar et al. (2025) yang fokus subjek Asia; iterasi rule berdasarkan UAT |
| R2 | Performa multimodal lambat akibat banyak visual | Sedang | Sedang | CDN/static caching, lazy-load image, optimasi format (WebP) |
| R3 | Produksi visual seed memakan waktu lebih lama dari estimasi | Sedang | Sedang | Mulai produksi visual paralel di Increment 1; gunakan template generator (Figma) |
| R4 | Integrasi AIML custom tag parser tidak stabil | Tinggi | Rendah | Unit test kuat untuk parser; gunakan lxml yang battle-tested |
| R5 | Mitra CV Four Vision Media terlambat menyediakan data katalog | Tinggi | Sedang | Backup dengan data dummy sintetis (sudah disepakati dalam proposal) |
| R6 | Browser pengguna lawas tidak mendukung fitur frontend | Rendah | Rendah | Polyfill Vue 3 + Tailwind; daftar minimal browser di NFR-PORT-01 |
| R7 | Hasil rekomendasi kurang relevan menurut UAT | Tinggi | Sedang | Buffer waktu di Increment 3 untuk penyetelan rule fuzzy |
| R8 | Rule AIML berkonflik (pattern overlap) | Sedang | Sedang | Linter AIML, testing pattern matching dengan corpus 50+ contoh per kategori |
| R9 | PII pengguna tidak sengaja tersimpan | Tinggi | Rendah | Audit log; anonimisasi sesi default |
| R10 | Defek di custom tag parser menyebabkan respons gagal render | Sedang | Sedang | Fallback: jika parser gagal, kirim sebagai teks polos dengan disclaimer |

---

## 17. ASUMSI DAN BATASAN

### 17.1 Asumsi

- Pengguna mampu menjawab pertanyaan profiling secara jujur.
- Mitra menyediakan data produk dengan kode HEX warna yang valid.
- Standar seasonal color theory yang digunakan adalah Nasr (2018) dengan empat tipe.

### 17.2 Batasan

- Tidak ada deteksi warna kulit otomatis berbasis citra.
- Antarmuka hanya web (bukan mobile native).
- Bahasa antarmuka: Bahasa Indonesia (versi awal).
- Tidak ada autentikasi pengguna — sistem berbasis sesi anonim.
- Tidak melakukan integrasi e-commerce penuh (cart/checkout/payment).

---

## 18. GLOSARIUM

| Istilah | Definisi |
|---|---|
| **AIML** | Bahasa markup berbasis XML yang digunakan untuk mendefinisikan pola percakapan dan respons dalam sistem chatbot. |
| **Color Brightness (CB)** | Tingkat kecerahan suatu warna dalam ruang HSV diwakili oleh komponen Value (V); diklasifikasikan dark, medium, light. |
| **Color Temperature (CT)** | Persepsi kehangatan/kesejukan warna berdasarkan komponen Hue dan Saturation; diklasifikasikan warm, cool, neutral. |
| **Custom AIML Tag** | Tag XML non-standar yang ditambahkan ke template AIML untuk memerintah backend menyisipkan visualisasi. |
| **Defuzzifikasi** | Proses mengubah nilai fuzzy menjadi nilai crisp (numerik tunggal). |
| **Fitzpatrick Scale** | Skala klasifikasi warna kulit dari Tipe I (very fair) hingga Tipe VI (dark brown). |
| **Fuzzy Inference System (FIS) Mamdani** | Sistem inferensi fuzzy dengan empat tahap: fuzzifikasi, evaluasi rule, agregasi, defuzzifikasi. |
| **Fuzzy Logic** | Pendekatan logika untuk menangani ketidakpastian dengan derajat keanggotaan [0, 1]. |
| **HSV (Hue, Saturation, Value)** | Model warna persepsi manusia: Hue (warna), Saturation (kemurnian), Value (kecerahan). |
| **Multimodal Response** | Respons chatbot yang mengandung lebih dari satu modalitas (mis. teks + gambar) dalam satu pesan. |
| **Quick Reply** | Tombol pintasan yang ditampilkan di antarmuka chat untuk respons cepat. |
| **Rank Order Centroid (ROC)** | Metode pembobotan kriteria berdasarkan urutan prioritas. |
| **RGB** | Model warna digital: Red, Green, Blue. |
| **Seasonal Color Theory** | Klasifikasi tipe warna kulit dan palet pakaian ke empat musim (Spring, Summer, Autumn, Winter). |
| **Simple Additive Weighting (SAW)** | Metode pengambilan keputusan multi-atribut dengan penjumlahan terbobot ternormalisasi. |
| **Singleton (Fuzzy)** | Output fuzzy berbentuk satu nilai numerik tunggal (bukan himpunan). |
| **Skin Tone** | Warna permukaan kulit; diklasifikasikan dengan skala Fitzpatrick I–VI. |
| **Undertone** | Warna dasar kulit (cool, neutral, warm) yang tidak berubah meski permukaan kulit berubah. |
| **Visual Asset** | File gambar (PNG/SVG/WebP) yang disimpan di tabel `visual_assets` dan dapat direferensikan oleh tag AIML. |
| **Y₁** | Output FIS Layer 1 — Seasonal Color Type pengguna (kontinu di [0, 3]). |
| **Y₂** | Output FIS Layer 2 — Suitability Score satu warna terhadap profil pengguna (di [0, 1]). |

---

**— Akhir Dokumen PRD —**

*Dokumen ini akan diperbarui sesuai feedback Seminar 2 dan UAT mitra. Versi terbaru disimpan di repository proyek dengan tag versi.*
