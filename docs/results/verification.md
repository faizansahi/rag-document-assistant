# Verification status

Local Windows execution on 7 September 2026 passed 8 tests with 95% statement coverage. Ruff lint, formatting, and source compilation passed. Raw reports are in this directory.

The live API uploaded a **2-page sample PDF**, created **2 chunks**, retrieved evidence, answered “The safety inspection occurs every Monday.” with a **manual.pdf, page 1** citation, reindexed, refused an unrelated query, and deleted the document. The screenshot above is the running Swagger interface; the full request workflow is saved as JSON.

Docker was unavailable on the local Windows machine. Docker Compose and PostgreSQL 16 were verified successfully on a GitHub-hosted Ubuntu runner.

[Successful CI run 34070962688](https://github.com/faizansahi/rag-document-assistant/actions/runs/34070962688) passed both the quality and containers jobs. The run includes dependency resolution, lint, formatting, tests, Compose validation, image build, container execution, and PostgreSQL checks.

The container uploaded the authored PDF, indexed it, returned a cited answer, reindexed, and deleted it using PostgreSQL metadata and local Qdrant.

[Downloaded container execution artifact](docker-demo.json) preserves the actual results from that run. These artifacts are separate from the local SQLite demo.

The test output retains upstream Starlette/httpx deprecation warnings; no tests were skipped because of them.
