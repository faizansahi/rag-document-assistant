# Architecture
PDF pages are extracted independently, normalized, chunked at 900 characters with 150-character overlap, embedded locally, and indexed in Qdrant. Retrieval score gates answer construction.
