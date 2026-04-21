# PRD — Seera Project
## Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit

---

| Atribut | Detail |
|---|---|
| **Dokumen** | Product Requirements Document (PRD) |
| **Versi** | v1.0.0 |
| **Tim** | Aisyah Naomi Kazzayara (231511001) · Annisa Suci Soleha (231511005) · Timothy Elroy (231511031) |
| **Kelas** | 3A — D3 Teknik Informatika, Politeknik Negeri Bandung |
| **Mitra** | CV Four Vision Media (Seera Project) |
| **Platform** | Web Application (Vue.js + FastAPI) |
| **Metodologi** | SDLC Incremental (Sommerville, 2016) |
| **Timeline** | Februari — Juni 2026 |

---

## Daftar Isi

1. [Ringkasan Produk](#1-ringkasan-produk)
2. [Tujuan & Rumusan Masalah](#2-tujuan--rumusan-masalah)
3. [Pengguna & Stakeholder](#3-pengguna--stakeholder)
4. [Arsitektur Sistem](#4-arsitektur-sistem)
5. [Algoritma Detail](#5-algoritma-detail)
6. [Fitur & Functional Requirements](#6-fitur--functional-requirements)
7. [Tech Stack & Skema Database](#7-tech-stack--skema-database)
8. [Increment Development Plan](#8-increment-development-plan)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Testing & Validasi](#10-testing--validasi)
11. [Batasan & Asumsi](#11-batasan--asumsi)
12. [Risiko & Mitigasi](#12-risiko--mitigasi)
13. [Referensi](#13-referensi)

---

## 1. Ringkasan Produk

Seera Project adalah aplikasi chatbot rekomendasi warna pakaian berbasis web yang dikembangkan untuk platform e-commerce CV Four Vision Media. Sistem menjawab masalah nyata yang teridentifikasi dari riset Oktaviani & Marsudi (2024): **88,9% remaja perempuan Indonesia tidak cocok memilih warna fashion**, dan **63,7% tidak mengetahui** cara memilih warna yang sesuai dengan karakteristik kulit mereka.

Solusi diimplementasikan melalui empat metode yang terintegrasi:

| Metode | Peran dalam Sistem |
|---|---|
| **AIML** | Antarmuka percakapan — profiling kulit user & edukasi seasonal color theory |
| **FIS Mamdani (2-layer)** | Menghitung kesesuaian warna produk dengan karakteristik kulit user |
| **ROC (Rank Order Centroid)** | Mengagregasi skor multi-warna menjadi satu skor per produk |
| **SAW (Simple Additive Weighting)** | Meranking produk berdasarkan warna, harga, rating, dan popularitas |

### Alur Produk Tingkat Tinggi

```
User berinteraksi via Chatbot (AIML)
         |
         v
Sistem menggali: Skin Tone (X1) + Undertone (X2)
         |
         v
FIS Layer 1 --> Seasonal Color Type (Y1)
         |
         v
Produk DB: Hex Warna --> HSV --> CT (X4) + CB (X5)
         |
         v
FIS Layer 2 --> Suitability Score Y2 per warna
         |
         v
ROC --> Skor_Produk (agregasi multi-warna)
         |
         v
SAW --> Ranked Product List
         |
         v
Chatbot menampilkan rekomendasi ke user
```

---

## 2. Tujuan & Rumusan Masalah

### 2.1 Rumusan Masalah

| ID | Masalah | Solusi |
|---|---|---|
| **M-01** | Pengguna kesulitan menentukan warna fashion yang sesuai karakteristik kulit | Sistem profiling via chatbot AIML |
| **M-02** | Tidak ada sistem rekomendasi berbasis multiple attribute | SAW mengintegrasikan 4 kriteria dalam satu skor ranking |
| **M-03** | Tidak ada antarmuka percakapan interaktif untuk rekomendasi fashion | Chatbot AIML memandu user layaknya konsultan warna digital |
| **M-04** | Pengguna belum memahami karakteristik kulit mereka sendiri | Modul edukasi seasonal color theory dalam chatbot |

### 2.2 Tujuan Sistem

1. Aplikasi merekomendasikan warna produk berdasarkan **skin tone, undertone, dan seasonal color type** pengguna.
2. Aplikasi menerapkan **Fuzzy Logic** untuk menghitung kesesuaian warna produk dengan kulit pengguna.
3. Aplikasi meranking produk menggunakan **SAW** berdasarkan warna, harga, rating, dan popularitas.
4. Aplikasi menyediakan **chatbot interaktif berbasis AIML** untuk memandu rekomendasi.
5. Aplikasi menyediakan **fitur edukatif** tentang skin tone, undertone, dan seasonal color type melalui chatbot.
6. Aplikasi menghasilkan bobot menggunakan **ROC** jika warna produk lebih dari satu.

---

## 3. Pengguna & Stakeholder

### 3.1 End User — Pembeli Seera

- **Profil**: Remaja/dewasa yang mengunjungi platform e-commerce Seera dan ingin rekomendasi warna pakaian.
- **Karakteristik**: Tidak familiar dengan konsep seasonal color theory; berinteraksi via teks; berbahasa Indonesia.
- **Kebutuhan utama**: Rekomendasi yang personal dan mudah dipahami tanpa pengetahuan fashion khusus.

### 3.2 Admin — CV Four Vision Media

- **Profil**: Tim Seera yang mengelola katalog produk.
- **Tanggung jawab**: Input produk baru (nama, harga, rating, unit terjual, kode hex warna, urutan warna dominan/sekunder/aksen).
- **Peran dalam UAT**: Menguji sistem dan memberikan feedback sebelum Sidang TA.

---

## 4. Arsitektur Sistem

### 4.1 Komponen Utama

```
+------------------------------------------------------------+
|                   FRONTEND (Vue.js 3)                      |
|    Antarmuka Chatbot   |   Tampilan Rekomendasi Produk     |
+------------------------------------------------------------+
                         | REST API (HTTP/JSON)
+------------------------------------------------------------+
|                    BACKEND (FastAPI)                       |
|                                                            |
|  +--------------+  +----------------+  +---------------+  |
|  | Modul AIML   |  |  Modul Fuzzy   |  | Modul SAW+ROC |  |
|  | (python-aiml)|  | (scikit-fuzzy) |  |               |  |
|  +--------------+  +----------------+  +---------------+  |
+------------------------------------------------------------+
                         | SQLAlchemy ORM
+------------------------------------------------------------+
|                  DATABASE (PostgreSQL)                     |
|  products | product_colors | fuzzy_rules | chat_sessions  |
+------------------------------------------------------------+
```

### 4.2 Alur Data End-to-End

```
User input (teks) --> AIML Parser --> Skin Tone (X1) + Undertone (X2)
    |
    v
FIS Layer 1:
  X1 + X2 --> Y1 (Seasonal Color Type)
  Nilai Y1 kontinu dalam [0, 3]
  Spring~0.5 | Summer~1.5 | Autumn~2.0 | Winter~2.5
    |
    v
DB Produk: Hex --> RGB --> HSV --> CT (X4) + CB (X5) [precomputed]
    |
    v
FIS Layer 2:
  Y1 (difuzzifikasi ulang) + CT + CB --> Y2 (Suitability Score per warna)
    |
    v  [IF produk memiliki > 1 warna]
ROC: w(k) = (1/n) x sum(1/j) --> Skor_Produk = sum(wk x Y2k)
    |
    v
SAW: Vi = 0.70xR(C1) + 0.15xR(C2) + 0.10xR(C3) + 0.05xR(C4)
    |
    v
Ranked Product List --> AIML Response --> User
```

---

## 5. Algoritma Detail

### 5.1 Konversi Hex ke RGB ke HSV

Warna produk disimpan sebagai kode Hex di database. Sistem mengkonversinya ke HSV untuk mendapatkan nilai H, S, V yang diperlukan dalam perhitungan CT dan CB. Konversi ini dilakukan **sekali saat produk didaftarkan** dan hasilnya disimpan permanen di database.

**Langkah-langkah konversi (Chernov et al., 2015):**

```
Input:  R, G, B dalam [0, 255]
Output: H dalam [0, 360], S dalam [0, 1], V dalam [0, 1]

Langkah 1 - Normalisasi:
  R' = R/255,  G' = G/255,  B' = B/255

Langkah 2 - Cmax, Cmin, Delta:
  Cmax  = max(R', G', B')
  Cmin  = min(R', G', B')
  Delta = Cmax - Cmin

Langkah 3 - Hitung V:
  V = Cmax

Langkah 4 - Hitung S:
  Jika Delta = 0  --> S = 0   (kasus akromatik)
  Jika Delta != 0 --> S = Delta / Cmax

Langkah 5 - Hitung H:
  Jika Delta = 0  --> H = 0 (tidak terdefinisi, tangani sebagai netral)
  Jika Cmax = R'  --> H = (1/6) x [(G'-B')/Delta mod 6]
  Jika Cmax = G'  --> H = (1/6) x [(B'-R')/Delta + 2]
  Jika Cmax = B'  --> H = (1/6) x [(R'-G')/Delta + 4]
  Jika H < 0      --> H = H + 360
```

**Contoh — Navy Blue (#1B3A6B):**

| Langkah | Operasi | Hasil |
|---|---|---|
| Input | R=27, G=58, B=107 | — |
| Normalisasi | 27/255, 58/255, 107/255 | R'=0.106, G'=0.227, B'=0.420 |
| Cmax/Cmin/Delta | max, min, selisih | Cmax=0.420, Cmin=0.106, Delta=0.314 |
| **H** | Cmax=B', rumus ke-3 | **H = 214°** |
| **S** | Delta/Cmax | **S = 0.748** |
| **V** | Cmax | **V = 0.420** |

---

### 5.2 Color Temperature (CT) dan Color Brightness (CB)

#### Color Temperature (CT) — Universe [0, 2]

CT merepresentasikan kehangatan atau kesejukan suatu warna, ditentukan oleh komponen H dan S (Perrett & Sprengelmeyer, 2021).

**Langkah 1 — Cek S:**
- Jika S = 0 maka CT = 1.0 (warna akromatik)
- Jika S > 0 lanjut ke Langkah 2

**Langkah 2 — Petakan H ke CT:**

| Zona H | Tipe | Rumus CT | Rentang CT |
|---|---|---|---|
| H dalam [90, 270] | Cool | CT = 0.8 x (1 - abs(H-210) / 60) | [0.0 – 0.8] |
| H dalam [0, 90] | Warm | CT = 1.2 + 0.8 x (1 - abs(H-45) / 45) | [1.2 – 2.0] |
| H dalam [270, 360] | Warm | CT = 1.2 + 0.8 x (1 - abs(H-345) / 15) | [1.2 – 2.0] |
| Transisi [90-150], [270-330] | Neutral | CT = 1.0 | 1.0 |

> **Catatan:** S = 0 berarti tidak ada komponen Hue (abu-abu/hitam/putih murni), diperlakukan sebagai neutral (Smith, 1978).

#### Color Brightness (CB) — Universe [0, 1]

CB = nilai V hasil konversi HSV (Chernov et al., 2015). Diklasifikasikan ke dalam tiga kategori: Dark (V rendah), Medium (V sedang), Light (V tinggi).

---

### 5.3 Variabel Fuzzy — Universum dan Parameter Membership Function

Semua fungsi keanggotaan menggunakan dua bentuk dasar (Mamdani & Assilian, 1975):

```
Triangular (a, b, c):
  mu(x) = 0                  jika x <= a atau x >= c
  mu(x) = (x - a) / (b - a)  jika a < x <= b  [lereng naik]
  mu(x) = (c - x) / (c - b)  jika b < x < c   [lereng turun]

Trapezoidal (a, b, c, d):
  mu(x) = 0                  jika x <= a atau x >= d
  mu(x) = (x - a) / (b - a)  jika a < x < b   [lereng naik]
  mu(x) = 1                  jika b <= x <= c  [plateau]
  mu(x) = (d - x) / (d - c)  jika c < x < d   [lereng turun]
```

#### Skin Tone (X1) — Universe [1, 6]

Berdasarkan skala Fitzpatrick (Nasr, 2018). Overlap antar himpunan mencerminkan transisi warna kulit yang bersifat gradual.

| Himpunan | Fungsi | Parameter | Karakteristik |
|---|---|---|---|
| Very Fair | Trapezoid | [1.0, 1.0, 1.3, 1.7] | Selalu cerah, tidak pernah menggelap |
| Fair | Triangular | [1.3, 2.0, 2.7] | Terkadang cerah, jarang menggelap |
| Medium Fair | Triangular | [2.3, 3.0, 3.7] | Terkadang cerah, terkadang menggelap |
| Moderate Brown | Triangular | [3.3, 4.0, 4.7] | Terkadang cerah, biasanya menggelap |
| Brown | Triangular | [4.3, 5.0, 5.7] | Jarang cerah, selalu menggelap |
| Dark Brown | Trapezoid | [5.3, 5.7, 6.0, 6.0] | Tidak pernah cerah, selalu menggelap |

#### Undertone (X2) — Universe [0, 2]

0 = Cool, 1 = Neutral, 2 = Warm.

| Himpunan | Fungsi | Parameter | Karakteristik |
|---|---|---|---|
| Cool | Trapezoid | [0.0, 0.0, 0.5, 0.8] | Nuansa pink, merah, atau biru |
| Neutral | Triangular | [0.6, 1.0, 1.4] | Kombinasi warm dan cool |
| Warm | Trapezoid | [1.2, 1.5, 2.0, 2.0] | Nuansa kuning atau golden |

#### Color Temperature (X4) — Universe [0, 2]

| Himpunan | Fungsi | Parameter | Plateau mu=1 | Zero mu=0 |
|---|---|---|---|---|
| Cool | Trapezoid | [0.0, 0.0, 0.5, 0.8] | CT dalam [0.0, 0.5] | CT >= 0.8 |
| Neutral | Triangular | [0.6, 1.0, 1.4] | CT = 1.0 | CT <= 0.6 atau >= 1.4 |
| Warm | Trapezoid | [1.2, 1.5, 2.0, 2.0] | CT dalam [1.5, 2.0] | CT <= 1.2 |

#### Color Brightness (X5) — Universe [0, 1]

| Himpunan | Fungsi | Parameter | Plateau mu=1 | Zero mu=0 |
|---|---|---|---|---|
| Dark | Trapezoid | [0.0, 0.0, 0.20, 0.40] | CB dalam [0.0, 0.20] | CB >= 0.40 |
| Medium | Triangular | [0.30, 0.50, 0.70] | CB = 0.50 | CB <= 0.30 atau >= 0.70 |
| Light | Trapezoid | [0.60, 0.80, 1.0, 1.0] | CB dalam [0.80, 1.0] | CB <= 0.60 |

---

### 5.4 FIS Layer 1 — Skin Tone + Undertone ke Seasonal Color Type

**Prinsip (Nasr, 2018):** kulit cerah + Cool = Summer | cerah + Warm = Spring | gelap + Cool = Winter | gelap + Warm = Autumn.

#### Output Y1 — Seasonal Color Type — Universe [0, 3]

Y1 bersifat kontinu (hasil weighted average), bukan nilai diskrit.

| Tipe Seasonal | Singleton | Karakteristik Kulit | Warna yang Cocok |
|---|---|---|---|
| Spring | 5 | Warm Undertone + Cerah | Warm + Light |
| Summer | 15 | Cool Undertone + Cerah | Cool + Light |
| Autumn | 20 | Warm Undertone + Gelap/Sedang | Warm + Dark/Medium |
| Winter | 25 | Cool Undertone + Gelap/Sedang | Cool + Dark/Medium |

#### 18 Rules FIS Layer 1

| Rule | Skin Tone | Undertone | Output Seasonal | Bobot |
|---|---|---|---|---|
| R1 | Very Fair | Cool | Summer | 10 |
| R2 | Fair | Cool | Summer | 10 |
| R3 | Medium Fair | Cool | Summer | 8 |
| R4 | Moderate Brown | Cool | Winter | 10 |
| R5 | Brown | Cool | Winter | 10 |
| R6 | Dark Brown | Cool | Winter | 10 |
| R7 | Very Fair | Warm | Spring | 10 |
| R8 | Fair | Warm | Spring | 10 |
| R9 | Medium Fair | Warm | Spring | 8 |
| R10 | Moderate Brown | Warm | Autumn | 10 |
| R11 | Brown | Warm | Autumn | 10 |
| R12 | Dark Brown | Warm | Autumn | 8 |
| R13 | Very Fair | Neutral | Summer | 7 |
| R14 | Fair | Neutral | Summer | 7 |
| R15 | Medium Fair | Neutral | Spring | 7 |
| R16 | Moderate Brown | Neutral | Autumn | 7 |
| R17 | Brown | Neutral | Autumn | 7 |
| R18 | Dark Brown | Neutral | Winter | 7 |

#### Empat Tahap Inferensi Mamdani Layer 1

```
Tahap 1 - Fuzzifikasi:
  Hitung mu setiap himpunan X1 dan X2.

Tahap 2 - Evaluasi Rules:
  alpha = min(mu_X1, mu_X2) x bobot_rule
  Hanya rule dengan alpha > 0 yang aktif.

Tahap 3 - Agregasi:
  Kumpulkan semua pasangan (alpha, singleton) dari rule aktif.

Tahap 4 - Defuzzifikasi (Weighted Average):
  Y1 = sum(alpha_i x s_i) / sum(alpha_i)
```

---

### 5.5 FIS Layer 2 — Seasonal + CT + CB ke Suitability Score

Y1 difuzzifikasi ulang di Layer 2 sehingga user di zona ambiguitas antara dua seasonal mengaktifkan rules dari keduanya secara proporsional.

#### Fuzzifikasi Y1 di Layer 2

| Himpunan | Fungsi | Parameter | Puncak mu=1 |
|---|---|---|---|
| Spring | Triangular | (0.0, 0.5, 1.0) | Y1 = 0.5 |
| Summer | Triangular | (0.5, 1.5, 2.0) | Y1 = 1.5 |
| Autumn | Triangular | (1.5, 2.0, 2.5) | Y1 = 2.0 |
| Winter | Triangular | (2.0, 2.5, 3.0) | Y1 = 2.5 |

#### Output Y2 — Suitability Score — Universe [0, 1]

| Kategori | Singleton | Kondisi CT dan CB | Makna |
|---|---|---|---|
| Not Suitable | 10 | CT berlawanan + CB berlawanan | Warna sangat tidak sesuai |
| Less Suitable | 35 | Salah satu berlawanan | Warna kurang sesuai |
| Suitable | 65 | Satu cocok, satu Neutral/parsial | Warna cukup sesuai |
| Very Suitable | 90 | CT cocok + CB cocok | Warna sangat sesuai |

> Singleton tidak menyentuh ekstrem 0 dan 1 — ini disengaja untuk memberi ruang gradasi pada hasil defuzzifikasi.

#### 36 Rules FIS Layer 2

**SPRING — butuh Warm + Light:**

| Rule | CT Warna | CB Warna | Suitability | Singleton |
|---|---|---|---|---|
| R1 | Warm | Light | Very Suitable | 90 |
| R2 | Warm | Medium | Suitable | 65 |
| R3 | Warm | Dark | Less Suitable | 35 |
| R4 | Neutral | Light | Suitable | 65 |
| R5 | Neutral | Medium | Suitable | 65 |
| R6 | Neutral | Dark | Less Suitable | 35 |
| R7 | Cool | Light | Less Suitable | 35 |
| R8 | Cool | Medium | Less Suitable | 35 |
| R9 | Cool | Dark | Not Suitable | 10 |

**SUMMER — butuh Cool + Light:**

| Rule | CT Warna | CB Warna | Suitability | Singleton |
|---|---|---|---|---|
| R10 | Cool | Light | Very Suitable | 90 |
| R11 | Cool | Medium | Suitable | 65 |
| R12 | Cool | Dark | Less Suitable | 35 |
| R13 | Neutral | Light | Suitable | 65 |
| R14 | Neutral | Medium | Suitable | 65 |
| R15 | Neutral | Dark | Less Suitable | 35 |
| R16 | Warm | Light | Less Suitable | 35 |
| R17 | Warm | Medium | Less Suitable | 35 |
| R18 | Warm | Dark | Not Suitable | 10 |

**AUTUMN — butuh Warm + Dark/Medium:**

| Rule | CT Warna | CB Warna | Suitability | Singleton |
|---|---|---|---|---|
| R19 | Warm | Dark | Very Suitable | 90 |
| R20 | Warm | Medium | Very Suitable | 90 |
| R21 | Warm | Light | Suitable | 65 |
| R22 | Neutral | Dark | Suitable | 65 |
| R23 | Neutral | Medium | Suitable | 65 |
| R24 | Neutral | Light | Less Suitable | 35 |
| R25 | Cool | Dark | Less Suitable | 35 |
| R26 | Cool | Medium | Less Suitable | 35 |
| R27 | Cool | Light | Not Suitable | 10 |

**WINTER — butuh Cool + Dark/Medium:**

| Rule | CT Warna | CB Warna | Suitability | Singleton |
|---|---|---|---|---|
| R28 | Cool | Dark | Very Suitable | 90 |
| R29 | Cool | Medium | Very Suitable | 90 |
| R30 | Cool | Light | Suitable | 65 |
| R31 | Neutral | Dark | Suitable | 65 |
| R32 | Neutral | Medium | Suitable | 65 |
| R33 | Neutral | Light | Less Suitable | 35 |
| R34 | Warm | Dark | Less Suitable | 35 |
| R35 | Warm | Medium | Less Suitable | 35 |
| R36 | Warm | Light | Not Suitable | 10 |

#### Empat Tahap Inferensi Mamdani Layer 2

```
Tahap 1 - Fuzzifikasi Y1, CT, CB:
  Hitung mu_seasonal dari Y1 menggunakan fungsi Triangular.
  Hitung mu_CT dan mu_CB menggunakan parameter di Bagian 5.3.

Tahap 2 - Evaluasi Rules:
  alpha = min(mu_CT, mu_CB) x mu_seasonal
  Semua rules dari seasonal yang mu_seasonal > 0 dievaluasi sekaligus.

Tahap 3 - Agregasi:
  Kumpulkan semua pasangan (alpha, singleton) dari seluruh rule aktif lintas seasonal.

Tahap 4 - Defuzzifikasi (Weighted Average):
  Y2 = sum(alpha_i x s_i) / sum(alpha_i)
```

#### Contoh Perhitungan: Pure Summer (Y1=1.50), Navy Blue (CT=0.747, CB=0.420)

```
Fuzzifikasi Y1=1.50:
  mu_Summer = 1.00  (tepat di puncak Tri(0.5, 1.5, 2.0))
  mu_Spring = mu_Autumn = mu_Winter = 0.00

Fuzzifikasi CT=0.747:
  mu_Cool    = (0.8 - 0.747) / (0.8 - 0.5) = 0.177
  mu_Neutral = (0.747 - 0.6) / (1.0 - 0.6) = 0.368
  mu_Warm    = 0.000

Fuzzifikasi CB=0.420:
  mu_Medium = (0.420 - 0.30) / (0.50 - 0.30) = 0.600

Rules aktif Summer (mu_Summer = 1.00):
  R11 (Cool^Medium): alpha = min(0.177, 0.600) x 1.00 = 0.177, singleton = 65
  R14 (Neutral^Medium): alpha = min(0.368, 0.600) x 1.00 = 0.368, singleton = 65

Defuzzifikasi:
  Y2 = (0.177 x 65 + 0.368 x 65) / (0.177 + 0.368)
     = 35.425 / 0.545
     = 0.649

Kesimpulan: Y2 = 0.649 --> Navy Blue SUITABLE untuk Pure Summer
```

---

### 5.6 ROC — Pembobotan Multi-Warna Produk

ROC (Rank Order Centroid) menghasilkan bobot prioritas berdasarkan urutan kepentingan (Barron & Barrett, 1996 dalam Mahdi et al., 2023).

**Formula:**

```
w(k) = (1/n) x sum[1/j]  untuk j = k sampai n
```

**Tabel bobot ROC:**

| n | w1 | w2 | w3 |
|---|---|---|---|
| 1 | 1.000 | — | — |
| 2 | 0.750 | 0.250 | — |
| 3 | 0.611 | 0.278 | 0.111 |

**Agregasi:**

```
Skor_Produk = w1 x Y2_warna1 + w2 x Y2_warna2 + w3 x Y2_warna3
```

`Skor_Produk` menjadi nilai **C1** pada tahap SAW. Jika produk hanya memiliki 1 warna, `Skor_Produk = Y2` langsung (w1 = 1.000).

---

### 5.7 SAW — Ranking Akhir Produk

#### Kriteria dan Bobot

| Kode | Kriteria | Sumber Nilai | Tipe | Bobot |
|---|---|---|---|---|
| C1 | Color Suitability Score | Output ROC | Benefit | **0.70** |
| C2 | Harga Produk | Database produk | Cost | **0.15** |
| C3 | Rating Produk | Database produk | Benefit | **0.10** |
| C4 | Popularitas (unit terjual) | Database produk | Benefit | **0.05** |

> Jika user tidak mengisi preferensi harga, C2 **dinonaktifkan** dan bobot direnormalisasi: C1=0.824, C3=0.118, C4=0.059.

#### Formula Normalisasi dan Nilai Preferensi

```
Normalisasi Benefit:  R(Cj) = x_ij / max(xj)
Normalisasi Cost:     R(Cj) = min(xj) / x_ij

Nilai Preferensi Akhir (Fishburn, 1967; Taherdoost, 2023):
  Vi = 0.70 x R(C1i) + 0.15 x R(C2i) + 0.10 x R(C3i) + 0.05 x R(C4i)
```

Produk dengan nilai Vi tertinggi menempati ranking teratas.

---

## 6. Fitur & Functional Requirements

| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| **FR-01** | Chatbot Profiling | Modul AIML menggali skin tone dan undertone user melalui percakapan multi-turn. | MUST |
| **FR-02** | Konversi Hex ke HSV | Mengkonversi kode hex warna produk ke nilai CT dan CB. Dijalankan sekali saat produk didaftarkan, hasil disimpan permanen di DB. | MUST |
| **FR-03** | FIS Layer 1 | Inferensi Mamdani (Skin Tone, Undertone) ke Y1 (Seasonal Color Type). 18 rules, defuzzifikasi Weighted Average. | MUST |
| **FR-04** | FIS Layer 2 | Inferensi Mamdani (Y1, CT, CB) ke Y2 (Suitability Score per warna). 36 rules; Y1 difuzzifikasi ulang untuk handle ambiguitas antar seasonal. | MUST |
| **FR-05** | ROC Weighting | Agregasi skor multi-warna menjadi satu Skor_Produk. Berlaku hanya jika produk memiliki lebih dari 1 warna. | MUST |
| **FR-06** | SAW Ranking | Perangkingan multi-kriteria produk. Bobot C1=0.70, C2=0.15, C3=0.10, C4=0.05. Harga adalah kriteria Cost. | MUST |
| **FR-07** | Tampilan Rekomendasi | Daftar produk ter-ranking dengan detail skor, warna, harga, rating, disertai penjelasan singkat kesesuaian warna. | MUST |
| **FR-08** | Modul Edukasi Chatbot | Penjelasan seasonal color theory, skin tone, undertone via AIML. User dapat bertanya definisi dan karakteristik tiap tipe. | SHOULD |
| **FR-09** | Admin Panel CRUD Produk | Input/edit produk: nama, deskripsi, harga, rating, popularitas, kode hex warna, urutan warna (dominan/sekunder/aksen). | SHOULD |
| **FR-10** | Preferensi Harga User | User dapat menonaktifkan kriteria harga (C2); sistem merenormalisasi bobot SAW secara otomatis. | COULD |

---

## 7. Tech Stack & Skema Database

### 7.1 Tech Stack

| Layer | Teknologi | Keterangan |
|---|---|---|
| **Frontend** | Vue.js 3 (Composition API) + Vite + Tailwind CSS | Antarmuka chatbot dan tampilan rekomendasi |
| **Backend** | Python 3.10+ + FastAPI + Pydantic | REST API, validasi data, routing |
| **Fuzzy Logic** | scikit-fuzzy | Implementasi FIS Mamdani Layer 1 & 2 |
| **AIML** | python-aiml | Interpreter chatbot berbasis pattern-template |
| **ORM** | SQLAlchemy + Alembic | Database access & migrasi skema |
| **Database** | PostgreSQL | Penyimpanan produk, warna, rules, sesi chat |
| **API Testing** | Postman | Test collections per endpoint |
| **UI/UX Design** | Figma | Wireframe dan prototyping antarmuka |
| **Version Control** | Git / GitHub | Manajemen kode dan kolaborasi tim |
| **Project Mgmt** | ProjectLibre | Gantt chart dan tracking milestone |

### 7.2 Skema Database Utama

```sql
-- Tabel produk utama
products (
  id             UUID PRIMARY KEY,
  name           VARCHAR(255),
  description    TEXT,
  price          DECIMAL(12,2),
  rating         DECIMAL(3,2),
  sold_count     INTEGER,
  category_id    UUID,
  created_at     TIMESTAMP
)

-- Warna per produk — CT & CB dihitung saat INSERT
product_colors (
  id             UUID PRIMARY KEY,
  product_id     UUID REFERENCES products,
  hex_code       CHAR(7),
  color_order    SMALLINT,      -- 1=dominan, 2=sekunder, 3=aksen
  h_value        DECIMAL(6,3),  -- Hue [0-360]
  s_value        DECIMAL(5,4),  -- Saturation [0-1]
  v_value        DECIMAL(5,4),  -- Value [0-1]
  ct_value       DECIMAL(5,4),  -- Color Temperature [0-2]
  cb_value       DECIMAL(5,4)   -- Color Brightness [0-1]
)

-- 18 rules FIS Layer 1
fuzzy_rules_layer1 (
  id              SERIAL PRIMARY KEY,
  skin_tone_set   VARCHAR(20),   -- very_fair, fair, ..., dark_brown
  undertone_set   VARCHAR(10),   -- cool, neutral, warm
  seasonal_output VARCHAR(10),   -- spring, summer, autumn, winter
  weight          SMALLINT       -- 7, 8, atau 10
)

-- 36 rules FIS Layer 2
fuzzy_rules_layer2 (
  id                  SERIAL PRIMARY KEY,
  seasonal_set        VARCHAR(10),   -- spring, summer, autumn, winter
  ct_set              VARCHAR(10),   -- cool, neutral, warm
  cb_set              VARCHAR(10),   -- dark, medium, light
  suitability_output  VARCHAR(20),   -- not_suitable, less_suitable, suitable, very_suitable
  singleton_value     SMALLINT       -- 10, 35, 65, atau 90
)

-- Sesi percakapan user
chat_sessions (
  id                   UUID PRIMARY KEY,
  user_id              UUID,
  skin_tone_value      DECIMAL(4,2),  -- nilai X1 [1-6]
  undertone_value      DECIMAL(4,2),  -- nilai X2 [0-2]
  seasonal_type        VARCHAR(10),
  y1_value             DECIMAL(5,3),  -- Y1 kontinu hasil FIS Layer 1
  price_pref_enabled   BOOLEAN DEFAULT TRUE,
  created_at           TIMESTAMP
)

-- Cache hasil rekomendasi
recommendations (
  id             UUID PRIMARY KEY,
  session_id     UUID REFERENCES chat_sessions,
  product_id     UUID REFERENCES products,
  skor_produk    DECIMAL(6,4),  -- output ROC, = C1 untuk SAW
  saw_score      DECIMAL(6,4),  -- nilai Vi final SAW
  rank           SMALLINT,
  created_at     TIMESTAMP
)
```

---

## 8. Increment Development Plan

| Increment | Periode | Deliverable | Milestone |
|---|---|---|---|
| **Studi Literatur & Req.** | Feb MG1 – Mar MG2 | Review AIML, Fuzzy, SAW, ROC; finalisasi proposal BAB I–III | **Seminar 1** (Mar MG3) |
| **Increment 1 — Modul Dasar** | Mar MG4 – Apr MG3 | AIML profiling · FIS Layer 1 & 2 · Hex ke HSV · PostgreSQL setup · FastAPI dasar · Vue.js UI awal | **Seminar 2** (Apr MG4) |
| **Increment 2 — Integrasi** | Mei MG1 – MG3 | ROC · SAW · Modul edukasi AIML · REST API integration · Frontend rekomendasi · Integration testing | **Seminar 3** (Mei MG4) |
| **Increment 3 — Finalisasi** | Jun MG1 – MG3 | Penyempurnaan UI/UX · Black Box Testing · Validasi fuzzy manual · UAT · Laporan TA final | **Sidang TA** (Jun MG4) |

### Detail Deliverable per Increment

**Increment 1 — Release: AIML + FIS + Backend + UI Awal**

- File AIML: profiling flow (skin tone & undertone), navigasi dasar
- Engine FIS Layer 1: 18 rules, 6 MF skin tone, 3 MF undertone, defuzzifikasi WA
- Engine FIS Layer 2: 36 rules, 4 MF Y1 seasonal, MF CT & CB, defuzzifikasi WA
- Script konversi hex ke HSV (precomputed saat insert produk)
- Schema PostgreSQL: products, product_colors, fuzzy_rules_l1, fuzzy_rules_l2
- FastAPI endpoints: /chat, /recommend, /products (CRUD dasar)
- Vue.js: komponen ChatWindow, MessageBubble, ProductCard

**Increment 2 — Release: SAW + ROC + Modul Edukasi**

- ROC calculator: menghasilkan Skor_Produk dari multi-warna
- SAW engine: normalisasi benefit/cost + weighted sum + sorting
- AIML extended: pola edukasi seasonal color theory, skin tone, undertone
- Postman collections untuk integration test semua endpoint
- Frontend: ranked product list dengan skor dan penjelasan kesesuaian

**Increment 3 — Release: Sistem Final + UAT**

- Bug fixing dari hasil testing Increment 2
- Optimasi performa (target respons kurang dari 2 detik)
- UAT dengan CV Four Vision Media (kuesioner + skenario use case)
- Laporan TA final BAB IV Implementasi + BAB V Pengujian

---

## 9. Non-Functional Requirements

| Kategori | Requirement | Target |
|---|---|---|
| **Performance** | Waktu respons chatbot per turn | Kurang dari 2 detik |
| **Performance** | Waktu komputasi FIS + SAW per request | Kurang dari 3 detik |
| **Akurasi** | Selisih output FIS vs perhitungan manual | Kurang dari 0.001 |
| **Reliability** | Tidak error pada semua kombinasi valid (6 skin tone x 3 undertone) | 100% coverage (18 kombinasi) |
| **Usability** | Alur percakapan chatbot dapat dipahami user baru tanpa panduan | UAT score >= 70% |
| **Maintainability** | Rules FIS dapat diperbarui melalui database tanpa deploy ulang | Admin-editable via DB |
| **Scalability** | Sistem dapat menangani ratusan produk dalam katalog | Tidak ada hard limit jumlah produk |
| **Compatibility** | Berjalan pada browser modern | Chrome, Firefox, Safari (ES2020+) |
| **Platform** | Web-only, tidak memerlukan instalasi aplikasi | Responsive web app |
| **Language** | Antarmuka chatbot dalam Bahasa Indonesia | Seluruh pola AIML dalam Bahasa Indonesia |

---

## 10. Testing & Validasi

### 10.1 Matriks Pengujian

| Jenis Pengujian | Cakupan | Metode | Target |
|---|---|---|---|
| **Black Box Testing** | Semua alur chatbot: profiling, edukasi, rekomendasi, edge cases | Test case input/output tanpa melihat internal code | Semua test case lulus |
| **Validasi FIS Manual** | Akurasi output Layer 1 & 2 vs perhitungan spreadsheet | Minimal 10 kasus uji representatif mencakup tiap kondisi seasonal | Selisih kurang dari 0.001 |
| **Validasi SAW Manual** | Kebenaran normalisasi benefit/cost dan ranking produk | Dataset 5–10 produk; bandingkan Vi sistem vs hitung tangan | Ranking identik |
| **Validasi ROC** | Kebenaran bobot untuk n=1, 2, 3 warna | Hitung w(k) manual, bandingkan dengan output sistem | Bobot identik |
| **Integration Testing** | Aliran data end-to-end dari input chatbot hingga output ranking | Postman API test collections per endpoint | Semua endpoint 200/201 OK |
| **UAT** | Kepuasan dan kegunaan sistem dari perspektif pengguna dan stakeholder | Kuesioner + skenario penggunaan bersama CV Four Vision Media | Skor kepuasan >= 70% |

### 10.2 Kasus Uji Kritis untuk Validasi Fuzzy

| Kasus | X1 | X2 | Y1 Expected | Catatan |
|---|---|---|---|---|
| Pure Summer | 2.0 (Fair) | 0.0 (Cool) | ~15 (Summer) | Boundary condition |
| Pure Autumn | 5.0 (Brown) | 2.0 (Warm) | ~20 (Autumn) | Boundary condition |
| Ambiguitas Summer–Autumn | 3.0 (Medium Fair) | 1.0 (Neutral) | antara 15–20 | Uji fuzzifikasi overlap |
| Very Fair + Cool | 1.0 (Very Fair) | 0.0 (Cool) | ~15 (Summer) | Plateau MF |
| Dark Brown + Neutral | 6.0 (Dark Brown) | 1.0 (Neutral) | mendekati 25 (Winter) | Ujung universum |

---

## 11. Batasan & Asumsi

### 11.1 Batasan Sistem

1. Aplikasi **tidak mencakup** proses transaksi e-commerce (keranjang belanja, checkout, payment gateway).
2. Penentuan skin tone dan undertone dilakukan berdasarkan **input teks user** — bukan melalui analisis citra atau deteksi kamera.
3. Aplikasi dikembangkan untuk **platform web** saja, bukan mobile native.
4. Data produk bersumber dari **katalog internal Seera Project** milik CV Four Vision Media.
5. Sistem mendukung **maksimal 3 warna per produk** untuk keperluan ROC (dominan, sekunder, aksen).
6. AIML berbasis aturan pola — **tidak menggunakan NLP/ML** untuk pemahaman bahasa natural.

### 11.2 Asumsi Pengembangan

1. Admin Seera menginput kode hex warna produk dengan **format dan nilai yang akurat**.
2. Data rating dan jumlah produk terjual sudah tersedia dan dikelola dalam database Seera.
3. **Urutan prioritas warna** (dominan/sekunder/aksen) ditentukan dan diverifikasi oleh admin saat input produk.
4. User berkomunikasi dengan chatbot dalam **Bahasa Indonesia**.
5. Nilai skin tone yang diinput user adalah hasil self-assessment berdasarkan panduan dalam chatbot.

---

## 12. Risiko & Mitigasi

| ID | Risiko | Dampak | Kemungkinan | Mitigasi |
|---|---|---|---|---|
| **R-01** | User salah mendeskripsikan skin tone sehingga Y1 tidak akurat | Tinggi | Tinggi | Sediakan modul edukasi sebelum profiling; tampilkan contoh deskriptif tiap tipe skin tone dalam chatbot |
| **R-02** | Kode hex produk salah di-input admin sehingga CT/CB salah | Sedang | Sedang | Preview warna saat admin input hex; validasi format hex (#RRGGBB) di API layer |
| **R-03** | Warna achromatic (S=0) — hitam/putih/abu — H tidak terdefinisi | Rendah | Rendah | Handler khusus: S=0 maka CT = 1.0 (neutral); lanjutkan FIS Layer 2 normal |
| **R-04** | Pola AIML tidak mencakup variasi input user yang tidak terprediksi | Sedang | Tinggi | Sediakan fallback response; tambah pola secara iteratif berdasarkan hasil pengujian |
| **R-05** | Integrasi 4 modul memakan waktu, risiko keterlambatan jadwal | Tinggi | Sedang | Mulai integration testing sejak Increment 1; gunakan Postman collections; pisahkan unit test tiap modul |
| **R-06** | Performa lambat pada dataset produk besar | Sedang | Rendah | Precompute CT & CB saat insert produk; cache hasil rekomendasi per sesi; index DB pada kolom kritis |
| **R-07** | Hasil UAT tidak mencapai target kepuasan 70% | Tinggi | Rendah | Lakukan mini-UAT di akhir Increment 2; perbaiki berdasarkan feedback sebelum UAT formal di Increment 3 |

---

## 13. Referensi

| Sumber | Konteks dalam Sistem |
|---|---|
| Nasr (2018) | Seasonal color theory (Spring/Summer/Autumn/Winter), prinsip 18 rules FIS Layer 1, 36 rules FIS Layer 2 |
| Fitzpatrick (1975) dalam Nasr (2018) | Klasifikasi 6 tipe skin tone, dasar universum X1 |
| Chernov et al. (2015) | Algoritma konversi RGB ke HSV; definisi Color Brightness (CB=V) |
| Perrett & Sprengelmeyer (2021) | Definisi Color Temperature; pemetaan Hue ke zona cool/warm |
| Mamdani & Assilian (1975) | Rumus fungsi keanggotaan Triangular dan Trapezoidal; mekanisme inferensi Mamdani |
| Saatchi (2024) | Framework FIS — fuzzifikasi, rule evaluation, defuzzifikasi |
| Barron & Barrett (1996) dalam Mahdi et al. (2023) | Formula Rank Order Centroid (ROC) |
| Fishburn (1967); Taherdoost (2023) | Metode Simple Additive Weighting (SAW), normalisasi benefit/cost |
| Zulrahman & Syahputra (2023) | Implementasi AIML untuk chatbot berbasis pattern-template |
| Smith (1978) | Penanganan kasus achromatic (S=0) dalam ruang warna HSV |
| Butarbutar et al. (2025) | Klasifikasi undertone 3 kategori; subjektivitas deteksi manual undertone |
| Sommerville (2016) | SDLC Incremental Model sebagai metodologi pengembangan |
| Oktaviani & Marsudi (2024) | Data latar belakang: 88,9% remaja Indonesia tidak cocok memilih warna fashion |

---

*Dokumen ini merupakan PRD resmi untuk pengembangan Seera Project Tugas Akhir KoTA 103, D3 Teknik Informatika POLBAN, Tahun Akademik 2025/2026.*
