import os
import tempfile
from pathlib import Path

# Configure stores before application modules are imported.
STORE = tempfile.TemporaryDirectory(prefix="rag-tests-")
root = Path(STORE.name)
os.environ["DATABASE_URL"] = f"sqlite:///{root / 'test.db'}"
os.environ["QDRANT_PATH"] = ":memory:"
os.environ["UPLOAD_DIR"] = str(root / "uploads")


def pytest_sessionfinish(session, exitstatus):
    from rag_assistant.db import engine

    engine.dispose()
    from rag_assistant.main import client

    client.close()
    STORE.cleanup()
