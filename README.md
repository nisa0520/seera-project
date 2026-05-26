# Seera Project - Chatbot Rekomendasi Warna Pakaian

Monorepo Seera berisi frontend Vue 3 dan backend FastAPI untuk chatbot rekomendasi warna pakaian berdasarkan warna kulit.

- `src/` - Frontend Vue 3 + Vite. Chatbot widget tampil di pojok kanan bawah dan terhubung ke API backend.
- `backend/` - FastAPI + SQLAlchemy 2.x + Alembic. Berisi fuzzy logic, ROC, AIML interpreter, rekomendasi produk, edukasi, feedback, dan API publik.
- `AIML/` - Mockup/artifact awal chatbot. Tidak dipakai langsung saat runtime aplikasi.
- `docker/` - Konfigurasi pendukung Docker, termasuk pgAdmin.

## Quickstart Dengan Docker

Cara ini menjalankan semua service sekaligus: PostgreSQL, pgAdmin, backend, dan frontend.

### 1. Jalankan Project

```bash
docker compose up --build
```

Saat container backend start, seed data akan otomatis dijalankan lewat:

```bash
python -m app.seed.run_seed
```

### 2. Buka Aplikasi

- Frontend: <http://localhost>
- Backend API docs: <http://localhost:8000/docs>
- Backend health check: <http://localhost:8000/health>
- pgAdmin: <http://localhost:5050>

Login pgAdmin:

```text
Email: admin@seera.local
Password: admin123
```

Database PostgreSQL Docker:

```text
Host: localhost
Port: 5432
Database: seera_db
User: seera
Password: seera_pass
```

### 3. Stop Project

```bash
docker compose down
```

Untuk menghapus volume database juga:

```bash
docker compose down -v
```

## Run Lokal Tanpa Docker

Gunakan cara ini kalau ingin menjalankan frontend dan backend secara manual saat development.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed.run_seed
uvicorn app.main:app --reload --port 8000
```

Default `DATABASE_URL` di aplikasi adalah SQLite:

```text
sqlite:///./seera_chatbot.db
```

Jika ingin memakai PostgreSQL lokal, ubah `backend/.env`:

```text
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/seera_chatbot
```

Backend lokal tersedia di:

- API docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### Frontend

Buka terminal baru dari root project:

```bash
npm install
npm run dev
```

Frontend lokal tersedia di:

```text
http://localhost:5173
```

Secara default frontend membaca API dari `VITE_API_BASE_URL`. Jika perlu, buat `.env` di root project:

```text
VITE_API_BASE_URL=http://localhost:8000
```

## Migration Dan Seed

Backend otomatis menjalankan `Base.metadata.create_all()` saat startup agar database kosong bisa langsung dipakai. Untuk workflow migration manual:

```bash
cd backend
alembic upgrade head
python -m app.seed.run_seed
```

Seed mencakup:

- AIML categories
- Education topics dan contents
- Categories, colors, dan dummy products

## Testing

```bash
cd backend
python -m pytest -q
```

## Build Frontend

```bash
npm run build
npm run preview
```

## Catatan

- Docker frontend memakai nginx dan meneruskan request `/api/` ke service backend.
- Backend Docker memakai PostgreSQL dari service `postgres`.
- Backend lokal dapat memakai SQLite tanpa setup database tambahan.
