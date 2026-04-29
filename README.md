# Seera Project — Color Recommendation Chatbot

Implementasi berdasarkan PRD `PRD_Seera_Project.md` dengan arsitektur:

- Frontend: Vue 3 + Vite + Tailwind
- Backend: FastAPI + SQLAlchemy + Alembic + PostgreSQL
- Engine: scikit-fuzzy (FIS Layer 1 & 2), ROC, SAW, konversi Hex→HSV→CT/CB
- Chatbot: python-aiml

## Fitur Utama (MVP)

- Chatbot profiling skin tone & undertone (Bahasa Indonesia, multi-turn)
- FIS Layer 1: Skin Tone + Undertone → Seasonal Type (Y1)
- FIS Layer 2: Seasonal + CT + CB → Suitability per warna (Y2)
- ROC untuk agregasi multi-warna produk
- SAW untuk ranking final produk
- Product CRUD dasar + seeded data contoh

## Struktur Proyek

- `src/` frontend Vue
- `backend/app/` backend FastAPI

## Menjalankan Frontend

```bash
npm install
npm run dev
```

Frontend berjalan di default Vite: `http://localhost:5173`.

## Menjalankan Backend (PostgreSQL + FastAPI)

Masuk ke folder backend lalu install dependency Python:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# salin konfigurasi environment
copy .env.example .env

# contoh isi .env
# DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/seera_db

uvicorn app.main:app --reload --port 8000
```

Backend API tersedia di `http://localhost:8000`.

## PostgreSQL + pgAdmin Online (via Browser)

Jalankan database dan pgAdmin dengan Docker Compose dari root project:

```bash
docker compose up -d
```

Service yang aktif:

- PostgreSQL: `localhost:5432`
- pgAdmin (web): `http://localhost:5050`

Login pgAdmin default:

- Email: `admin@seera.com`
- Password: `admin123`

Saat menambahkan server di pgAdmin:

- Name: `Seera PostgreSQL`
- Hostname/address: `postgres`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Maintenance DB: `seera_db`

### Akses dari luar (online/public)

Jika deploy di VPS/cloud, pgAdmin bisa diakses online lewat `http://IP_SERVER:5050` dan PostgreSQL lewat `IP_SERVER:5432` (untuk pgAdmin desktop/aplikasi lain).

Pastikan firewall/security group membuka port:

- `5050/tcp` untuk pgAdmin web
- `5432/tcp` untuk PostgreSQL

Disarankan batasi IP yang boleh akses (jangan open ke seluruh internet di production).

## Database Migration (Alembic)

Jika ingin migration versioned (disarankan):

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

## Konfigurasi Environment Frontend

Salin `.env.example` menjadi `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Endpoint Utama Backend

- `POST /chat` — chatbot profiling + edukasi
- `POST /recommend` — generate ranking rekomendasi
- `GET /products` — list produk
- `POST /products` — tambah produk baru
- `GET /health` — health check

## Akses Fitur Advisor di Frontend

- Buka halaman `/advisor`
- Jalankan chat: ketik `mulai profiling`, lalu isi skin tone (1-6) dan undertone (cool/neutral/warm)
- Klik tombol **Generate Rekomendasi**
