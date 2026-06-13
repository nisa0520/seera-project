# Seera Chatbot Backend

FastAPI backend untuk Chatbot Rekomendasi Warna Pakaian Berdasarkan Warna Kulit.

## Stack

- Python 3.10+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL (SQLite untuk lokal/dev)
- Pydantic 2.x

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
```

`DATABASE_URL` default ke SQLite lokal (`sqlite:///./seera_chatbot.db`). Untuk PostgreSQL:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/seera_chatbot
```

## Migration & seed

```bash
alembic upgrade head
python -m app.seed.run_seed
```

Saat startup FastAPI juga otomatis menjalankan `Base.metadata.create_all()` agar bisa langsung dipakai.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs>

## Tests

```bash
pytest -q
```
