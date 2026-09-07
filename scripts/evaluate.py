"""Upload an authored sample PDF to a running API and preserve cited answers."""

import argparse
import html
import json
from pathlib import Path

import httpx
from reportlab.pdfgen import canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / "docs/results"
    sample = root / "docs/samples/manual.pdf"
    output.mkdir(parents=True, exist_ok=True)
    sample.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(sample))
    pdf.setTitle("Fictional warehouse manual - test fixture")
    pdf.drawString(50, 750, "Fictional warehouse manual - sample data only.")
    pdf.drawString(50, 710, "The safety inspection occurs every Monday. Helmets are mandatory.")
    pdf.showPage()
    pdf.drawString(50, 750, "Emergency contact is the shift supervisor.")
    pdf.save()
    records = []
    with httpx.Client(base_url=args.base_url, timeout=60, trust_env=False) as api:

        def request(method, path, **kwargs):
            response = api.request(method, path, **kwargs)
            response.raise_for_status()
            result = response.json() if response.content else None
            records.append(
                {"method": method, "path": path, "status": response.status_code, "response": result}
            )
            return result

        with sample.open("rb") as source:
            upload = request(
                "POST", "/documents", files={"file": ("manual.pdf", source, "application/pdf")}
            )
        assert upload["pages"] == 2 and upload["chunks"] == 2
        request("GET", "/documents")
        question = "When does the safety inspection occur?"
        answer = request("POST", "/ask", json={"question": question})
        assert "Monday" in answer["answer"]
        assert answer["citations"][0]["page"] == 1
        request("GET", "/debug/retrieval", params={"q": question})
        request("POST", f"/documents/{upload['id']}/reindex")
        fallback = request("POST", "/ask", json={"question": "xylophone quasar nebula"})
        assert fallback["citations"] == []
        request("DELETE", f"/documents/{upload['id']}")
    (output / "demo.json").write_text(
        json.dumps({"question": question, "answer": answer, "workflow": records}, indent=2) + "\n"
    )
    citation_rows = "".join(
        f"<li>{html.escape(c['filename'])}, page {c['page']} (score {c['score']:.3f})</li>"
        for c in answer["citations"]
    )
    report = f"""<!doctype html><html lang="en"><meta charset="utf-8">
    <title>Document question and cited answer</title>
    <style>body{{font:20px/1.6 system-ui;max-width:900px;margin:50px;color:#172b3a}}
    h1{{font-size:30px}}blockquote{{border-left:4px solid #187c9a;padding:16px 24px;
    background:#f1f6f8;margin:20px 0}}small{{color:#526673}}</style>
    <h1>Document question and cited answer</h1>
    <small>Recorded FastAPI response · authored sample PDF · extractive answer</small>
    <p><strong>Question</strong><br>{html.escape(question)}</p>
    <blockquote>{html.escape(answer["answer"])}</blockquote>
    <h2>Sources returned by the API</h2><ul>{citation_rows}</ul>
    <p>Upload: {upload["pages"]} pages, {upload["chunks"]} indexed chunks.</p>
    <small>Generated from the same live execution as demo.json. This is a result report,
    not an application interface or an accuracy evaluation.</small></html>"""
    (output / "answer.html").write_text(report, encoding="utf-8")
    print(json.dumps({"question": question, "answer": answer, "steps": len(records)}, indent=2))


if __name__ == "__main__":
    main()
