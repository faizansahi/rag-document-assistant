# Engineering decisions

## Accepted baseline

Hashed token vectors offer a deterministic, offline baseline. They represent lexical overlap rather than learned semantic meaning. Extractive answers expose their source; the score threshold and confidence labels are heuristics, not calibrated correctness probabilities.

## Testing strategy

Keep deterministic domain tests separate from HTTP/database integration and real model demos. Unit-test stubs are never presented as model evidence. Capture actual responses and preserve the commands needed to reproduce them.

## Tradeoffs

There is no generative LLM, OCR, authentication, or evaluated semantic embedding model. Hash collisions and irrelevant shared terms can produce poor retrieval. The three stores are not transactionally coordinated; interrupted ingestion/reindexing can require cleanup. Local Qdrant requires a single process/worker. The evidence filter cannot guarantee answer correctness.

## Next steps

Evaluate retrieval on a labeled question set, add learned multilingual embeddings, coordinate ingestion recovery, and support authenticated document ownership.
