# API
Use `/docs` for Swagger and `/openapi.json` for the machine-readable contract.

| Method | Route | Behavior |
|---|---|---|
| GET | /health | Process liveness and store kind |
| POST | /documents | Multipart PDF upload, returning ID, pages, and chunks |
| GET | /documents | Persisted document metadata |
| DELETE | /documents/{id} | Remove metadata, vectors, and stored PDF |
| POST | /documents/{id}/reindex | Rebuild vectors from the stored PDF |
| POST | /ask | Question, optional limit (1–20); answer and citations |
| GET | /debug/retrieval | q (3–2,000 characters), limit (1–20), scored hits |

Uploads are limited to 20 MB of PDF bytes. Non-PDF inputs return 415; unreadable or text-free PDFs return 422; oversized uploads return 413. Missing documents return 404; reindexing without the original file returns 409.

Citations carry filename, page, and retrieval score. Confidence is a heuristic band, not a correctness probability. If no qualifying source sentence exists, the answer is `Insufficient evidence in the uploaded documents.` with empty citations.

[Recorded upload/retrieval/answer/reindex/delete workflow](results/demo.json).
