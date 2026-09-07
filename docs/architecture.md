# Architecture

```mermaid
flowchart LR
  PDF[Sample PDF] --> Parse[pypdf pages]
  Parse --> Chunk[900-character chunks / 150 overlap]
  Chunk --> Embed[384-dimensional token hashing]
  Embed --> Q[(Qdrant)]
  Parse --> SQL[(Document metadata)]
  Ask[Question] --> Embed
  Q --> Hits[Scored retrieval]
  Hits --> Gate[Evidence and term overlap filter]
  Gate --> Answer[Extracted answer and page citations]
```

Page numbers stay attached to chunks through vector storage. Questions use the same token-hash function. SQL metadata and original files are stored separately from Qdrant.

See [design decisions](decisions.md) for tradeoffs.
