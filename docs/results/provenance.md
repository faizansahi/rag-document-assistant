# Evidence provenance
`../samples/manual.pdf` is an authored two-page fictional manual created by ReportLab. It contains no private or customer information.

`demo.json` records a real Uvicorn HTTP workflow: upload, SQL metadata listing, parsing/chunking/indexing results, retrieval, cited answer, reindexing, insufficient-evidence answer, and deletion. The local run used SQLite and local Qdrant. `../images/swagger-api.png` is a real browser screenshot of the running API.

Reproduce with `python scripts/evaluate.py` against a fresh API instance. Answer text is extracted from the sample PDF.

`answer.html` renders the actual answer and citations. `../images/rag-answer.png` is a browser capture of that result report, not an application UI.
