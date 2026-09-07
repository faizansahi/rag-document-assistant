# Verification status

Local Windows execution on 7 September 2026 passed 8 tests with 95% statement coverage. Ruff lint, formatting, and source compilation passed. Raw reports are in this directory.

The live API uploaded a **2-page sample PDF**, created **2 chunks**, retrieved evidence, answered “The safety inspection occurs every Monday.” with a **manual.pdf, page 1** citation, reindexed, refused an unrelated query, and deleted the document. The screenshot above is the running Swagger interface; the full request workflow is saved as JSON.

Docker and PostgreSQL execution were unavailable locally. GitHub Actions container verification is pending publication; this record will be updated after an actual run.

The test output retains upstream Starlette/httpx deprecation warnings; no tests were skipped because of them.
