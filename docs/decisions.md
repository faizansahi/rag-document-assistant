# Retrieval decisions

PDF pages are split into 900-character windows with 150-character overlap. Page boundaries are retained for citations. Character cuts can split sentences; there is no layout-aware table handling.

Normalized signed token hashes produce 384-dimensional vectors for cosine search in Qdrant. This offline lexical baseline needs no trained model but can miss paraphrases and suffer hash collisions.

Hits below the configured threshold (0.18 by default) are filtered individually. The answer builder selects up to three distinct source sentences with question-term overlap and cites only used passages. Confidence bands are heuristics, not accuracy probabilities. No qualifying sentence means an insufficient-evidence answer.

SQL metadata, local Qdrant, and original PDFs are separate stores. They must be backed up together. A failure between writes can leave partial state, and reindexing needs the source PDF. Local Qdrant requires one process. Recovery and a labeled question set should precede broader deployment.
