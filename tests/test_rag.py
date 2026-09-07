import io

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from rag_assistant.core import chunk_pages, embed, grounded_answer
from rag_assistant.main import COLLECTION, app, client


def pdf_bytes():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(72, 750, "The safety inspection occurs every Monday. Helmets are mandatory.")
    pdf.showPage()
    pdf.drawString(72, 750, "Emergency contact is the shift supervisor.")
    pdf.save()
    return buffer.getvalue()


def setup_function():
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)


def test_upload_ask_citation_delete_flow():
    with TestClient(app) as api:
        uploaded = api.post(
            "/documents", files={"file": ("manual.pdf", pdf_bytes(), "application/pdf")}
        )
        assert uploaded.status_code == 201 and uploaded.json()["pages"] == 2
        answer = api.post(
            "/ask", json={"question": "When does the safety inspection occur?"}
        ).json()
        assert answer["answer"] != "Insufficient evidence in the uploaded documents."
        assert (
            answer["citations"][0]["filename"] == "manual.pdf"
            and answer["citations"][0]["page"] == 1
        )
        assert api.get("/debug/retrieval?q=helmets").status_code == 200
        assert (
            api.post(f"/documents/{uploaded.json()['id']}/reindex").json()["status"] == "reindexed"
        )
        assert api.delete(f"/documents/{uploaded.json()['id']}").status_code == 204


def test_low_evidence_fallback_and_chunk_overlap():
    assert (
        grounded_answer("unrelated", [], 0.2)["answer"]
        == "Insufficient evidence in the uploaded documents."
    )
    assert len(embed("repeatable local embeddings")) == 384
    assert len(chunk_pages(["word " * 400])) > 1


def test_rejects_non_pdf():
    with TestClient(app) as api:
        assert (
            api.post("/documents", files={"file": ("x.txt", b"hello", "text/plain")}).status_code
            == 415
        )
