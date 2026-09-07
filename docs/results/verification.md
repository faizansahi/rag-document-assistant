# Executed checks

On 7 September 2026, Python 3.12.6 on Windows passed **8 tests** with
**95% statement coverage**. Ruff lint, formatting checks, dependency resolution,
`pip check`, and source compilation passed. The API demos import and run the application;
compilation alone is not a runtime import test.

Uploaded the authored two-page PDF, indexed two chunks, retrieved passages, answered with a page-1 citation, reindexed, returned no citations for an unrelated question, and deleted the document. The answer image captures a report rendered from these responses.

[Actual local responses](demo.json) · [Test report](tests.txt) · [Check exit codes](checks.json)

Absolute virtual-environment paths in reports are replaced with `<venv>` for portability.
The test report retains upstream FastAPI/Starlette deprecation warnings.

Docker is unavailable on the local Windows machine. Container checks run separately
on GitHub-hosted Ubuntu with PostgreSQL 16. The current workflow is linked from the README;
the final container evidence is recorded below after its run completes.
