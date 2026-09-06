import io
import os
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader
from qdrant_client import QdrantClient, models
from sqlalchemy import select

from .core import DIMENSIONS, chunk_pages, embed, grounded_answer
from .db import DocumentRecord, Session

COLLECTION = "document_chunks"
client = QdrantClient(path=os.getenv("QDRANT_PATH", ":memory:"))
documents: dict[str, dict] = {}
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


def ensure_collection():
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            COLLECTION,
            vectors_config=models.VectorParams(size=DIMENSIONS, distance=models.Distance.COSINE),
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_collection()
    yield


app = FastAPI(title="RAG Document Assistant", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "vector_store": "qdrant"}


@app.post("/documents", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(415, "Only PDF documents are supported")
    content = await file.read()
    if len(content) > 20_000_000:
        raise HTTPException(413, "PDF exceeds 20 MB")
    try:
        pages = [page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages]
    except Exception as exc:
        raise HTTPException(422, "Unreadable PDF") from exc
    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(422, "PDF contains no extractable text")
    document_id = str(uuid.uuid4())
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, f"{document_id}.pdf"), "wb") as stored:
        stored.write(content)
    ensure_collection()
    points = []
    for chunk in chunks:
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embed(chunk.text),
                payload={
                    "document_id": document_id,
                    "filename": file.filename,
                    "page": chunk.page,
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                },
            )
        )
    client.upsert(COLLECTION, points=points, wait=True)
    documents[document_id] = {
        "id": document_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "created_at": datetime.now(UTC).isoformat(),
    }
    with Session.begin() as database:
        database.add(
            DocumentRecord(
                id=document_id,
                filename=file.filename,
                pages=len(pages),
                chunks=len(chunks),
            )
        )
    return documents[document_id]


@app.get("/documents")
def list_documents():
    with Session() as database:
        return [
            {
                "id": row.id,
                "filename": row.filename,
                "pages": row.pages,
                "chunks": row.chunks,
                "created_at": row.created_at,
            }
            for row in database.scalars(select(DocumentRecord)).all()
        ]


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str):
    with Session.begin() as database:
        record = database.get(DocumentRecord, document_id)
        if record is None:
            raise HTTPException(404, "Document not found")
        database.delete(record)
    client.delete(
        COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            )
        ),
    )
    documents.pop(document_id, None)
    path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    if os.path.exists(path):
        os.remove(path)


@app.post("/documents/{document_id}/reindex")
def reindex_document(document_id: str):
    with Session() as database:
        record = database.get(DocumentRecord, document_id)
        if record is None:
            raise HTTPException(404, "Document not found")
        filename = record.filename
    path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    if not os.path.exists(path):
        raise HTTPException(409, "Original PDF is unavailable for re-indexing")
    pages = [page.extract_text() or "" for page in PdfReader(path).pages]
    chunks = chunk_pages(pages)
    client.delete(
        COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            )
        ),
    )
    client.upsert(
        COLLECTION,
        points=[
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embed(chunk.text),
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "page": chunk.page,
                    "chunk_index": chunk.index,
                    "text": chunk.text,
                },
            )
            for chunk in chunks
        ],
        wait=True,
    )
    return {"id": document_id, "chunks": len(chunks), "status": "reindexed"}


def retrieve(question: str, limit: int) -> list[dict]:
    ensure_collection()
    result = client.query_points(COLLECTION, query=embed(question), limit=limit, with_payload=True)
    return [{**point.payload, "score": point.score} for point in result.points]


@app.post("/ask")
def ask(payload: AskRequest):
    return grounded_answer(payload.question, retrieve(payload.question, payload.limit))


@app.get("/debug/retrieval")
def debug_retrieval(q: str, limit: int = 5):
    return {"query": q, "hits": retrieve(q, min(max(limit, 1), 20))}
