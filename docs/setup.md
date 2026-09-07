# Setup

## Local execution

Use Python 3.12+ and a separate virtual environment. Install `python -m pip install -e ".[dev]"`. Copy `.env.example` to `.env` only when customizing defaults; settings are read at process startup.

```bash
uvicorn rag_assistant.main:app --reload
```

Use one Uvicorn worker because local Qdrant takes an exclusive file lock. Back up metadata, vectors, and original PDFs together.

## Reproduce evidence

Use a fresh database and a running API:

```bash
python scripts/evaluate.py
```

The script saves actual JSON in `docs/results/` and creates an authored PDF in `docs/samples/`. Rerunning replaces the saved demo artifacts. Swagger screenshots were captured from running Uvicorn servers with a headless browser.

## PostgreSQL and Docker

Set a unique URL-safe `POSTGRES_PASSWORD` in your ignored `.env`. Compose requires it and supplies the internal connection URL. Start with `docker compose up --build`. Persistent volumes survive ordinary `docker compose down`.

Compose persists SQL metadata, uploaded PDFs, and local Qdrant data in separate volumes.

## Validate

```bash
ruff format --check .
ruff check .
pytest --cov=rag_assistant --cov-report=term-missing
python -m pip check
```

See [verification status](results/verification.md) for environment limits and CI evidence. No paid API credentials are required.
