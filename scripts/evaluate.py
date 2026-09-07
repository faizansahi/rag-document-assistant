"""Upload an authored sample PDF to a running API and preserve cited answers."""

import argparse
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
    pdf.setTitle("Fictional warehouse manual - portfolio test fixture")
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
    print(json.dumps({"question": question, "answer": answer, "steps": len(records)}, indent=2))


if __name__ == "__main__":
    main()
