# Seera Project — Chatbot Rekomendasi Warna Pakaian

Aplikasi monorepo:

- `backend/` — FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL (SQLite untuk lokal). Berisi seluruh implementasi PRD: Fuzzy Logic Layer 1 & 2, ROC, AIML interpreter, education, feedback, dan API publik.
- `src/` — Frontend Vue 3 (existing landing). Chatbot widget melayang di pojok kanan bawah pada **semua halaman** dan terhubung ke backend.
- `AIML/` — Mockup React asli (tidak dipakai runtime). Hanya bagian percakapan yang dipindahkan ke `src/components/chatbot/`.

## Quickstart

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m app.seed.run_seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
npm install
npm run dev
```

Buka `http://localhost:5173`. Klik tombol kecil di pojok kanan bawah untuk membuka chatbot Seera.

### Tests

```bash
cd backend
python -m pytest -q
```

## Catatan teknis

- `DATABASE_URL` default: `sqlite:///./seera_chatbot.db`. Untuk PostgreSQL set di `backend/.env`.
- Saat startup FastAPI menjalankan `Base.metadata.create_all()` agar bisa langsung dipakai. Migration Alembic tetap authoritative untuk produksi (`alembic upgrade head`).
- Override base URL backend dari frontend: set `VITE_API_BASE_URL` di `.env` proyek root (mis. `VITE_API_BASE_URL=http://localhost:8000`).
