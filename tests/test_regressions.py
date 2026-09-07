import pytest
from fastapi.testclient import TestClient

from rag_assistant.core import chunk_pages, grounded_answer
from rag_assistant.main import app


@pytest.mark.parametrize(("size", "overlap"), [(0, 0), (100, 100), (100, -1)])
def test_invalid_chunk_parameters(size, overlap):
    with pytest.raises(ValueError):
        chunk_pages(["text"], size, overlap)


def test_weak_hits_never_enter_answer_or_citations():
    hits = [
        {"text": "Inspection happens Monday.", "score": 0.7, "filename": "manual.pdf", "page": 1},
        {"text": "Inspection happens Friday.", "score": 0.01, "filename": "wrong.pdf", "page": 2},
    ]
    answer = grounded_answer("When is inspection?", hits)
    assert answer["answer"] == "Inspection happens Monday."
    assert [c["filename"] for c in answer["citations"]] == ["manual.pdf"]


def test_invalid_pdf_and_query_limits():
    with TestClient(app) as api:
        assert (
            api.post(
                "/documents", files={"file": ("bad.pdf", b"not a pdf", "application/pdf")}
            ).status_code
            == 422
        )
        assert (
            api.get("/debug/retrieval", params={"q": "inspection", "limit": -1}).status_code == 422
        )
        assert api.delete("/documents/missing").status_code == 404
