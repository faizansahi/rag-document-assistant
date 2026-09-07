"""Verify a running container API using fictional/public fixtures."""

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"
RECORDS = []


def request(method, path, payload=None, file=None):
    headers = {}
    content = None
    if payload is not None:
        content = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if file:
        filename, media_type, data = file
        boundary = "portfolio-container-check"
        content = (
            (
                f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
                f'filename="{filename}"\r\nContent-Type: {media_type}\r\n\r\n'
            ).encode()
            + data
            + f"\r\n--{boundary}--\r\n".encode()
        )
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    query = urllib.request.Request(BASE + path, data=content, headers=headers, method=method)
    with urllib.request.urlopen(query, timeout=300) as response:
        value = response.read()
        result = json.loads(value) if value else None
        RECORDS.append(
            {"method": method, "path": path, "status": response.status, "response": result}
        )
        return result


def main():
    for attempt in range(90):
        try:
            request("GET", "/health")
            break
        except (urllib.error.URLError, ConnectionError):
            if attempt == 89:
                raise
            time.sleep(1)
    upload = request(
        "POST",
        "/documents",
        file=("manual.pdf", "application/pdf", (ROOT / "docs/samples/manual.pdf").read_bytes()),
    )
    assert upload["pages"] == 2
    answer = request("POST", "/ask", {"question": "When does the safety inspection occur?"})
    assert "Monday" in answer["answer"] and answer["citations"][0]["page"] == 1
    request("POST", f"/documents/{upload['id']}/reindex")
    request("DELETE", f"/documents/{upload['id']}")
    output = ROOT / "docs/results/docker-demo.json"
    output.write_text(
        json.dumps({"database": "PostgreSQL 16 via Compose", "requests": RECORDS}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Container API workflow passed; output:", output.name)


if __name__ == "__main__":
    main()
